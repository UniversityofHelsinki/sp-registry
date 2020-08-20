import logging
import re

from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rr.models.attribute import Attribute
from rr.models.certificate import Certificate, certificate_validator
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint, endpoint_validator
from rr.models.nameidformat import NameIDFormat
from rr.models.redirecturi import RedirectUri, redirecturi_validator
from rr.models.oidc import GrantType, OIDCScope, ResponseType
from rr.models.serviceprovider import ServiceProvider, SPAttribute, get_field_names, server_names_validator
from rr.models.serviceprovider import new_ldap_entity_id_from_name
from rr.models.usergroup import UserGroup
from rr.serializers.certificate import CertificateLimitedSerializer
from rr.serializers.common import ActiveListSerializer
from rr.serializers.contact import ContactLimitedSerializer
from rr.serializers.endpoint import EndpointLimitedSerializer
from rr.serializers.redirecturi import RedirectUriLimitedSerializer
from rr.utils.missing_data import get_missing_sp_data
from rr.utils.serviceprovider import create_sp_history_copy

logger = logging.getLogger(__name__)


def _update_spattributes(validated_data, instance, user, modified):
    if 'spattribute_set' in validated_data:
        attributes = validated_data.pop('spattribute_set')
        removed_attributes = instance.spattribute_set.filter(end_at=None)
        for attribute in attributes:
            if not SPAttribute.objects.filter(sp=instance, attribute=attribute['attribute'], end_at=None).count():
                modified = True
                spattribute = SPAttribute.objects.create(sp=instance, **attribute)
                logger.info("Attribute {attribute} requested for {sp} by {user}"
                            .format(attribute=spattribute.attribute, sp=instance, user=user))
                removed_attributes = removed_attributes.exclude(pk=spattribute.pk)
            else:
                removed_attributes = removed_attributes.exclude(attribute__friendlyname=attribute['attribute'])
        if removed_attributes:
            modified = True
            for attribute in removed_attributes:
                attribute.end_at = timezone.now()
                attribute.save()
                logger.info("Attribute {attribute} removed from {service} by {user}"
                            .format(attribute=attribute.attribute, service=attribute.sp, user=user))
    return modified


def _update_certificates(validated_data, instance, user, modified):
    if 'certificates' in validated_data:
        certificates = validated_data.pop('certificates')
        removed_certificates = instance.certificates.filter(end_at=None)
        for certificate in certificates:
            certificate_instance, created = Certificate.objects.get_or_create(
                sp=instance, end_at=None, **certificate)
            if created:
                modified = True
                logger.info("Certificate added for {service} by {user}"
                            .format(service=instance, user=user))
            removed_certificates = removed_certificates.exclude(pk=certificate_instance.pk)
        if removed_certificates:
            modified = True
            for certificate in removed_certificates:
                certificate.end_at = timezone.now()
                certificate.save()
                logger.info("Certificate removed from {service} by {user}"
                            .format(service=certificate.sp, user=user))
    return modified


def _update_contacts(validated_data, instance, user, modified):
    if 'contacts' in validated_data:
        contacts = validated_data.pop('contacts')
        removed_contacts = instance.contacts.filter(end_at=None)
        for contact in contacts:
            contact_instance, created = Contact.objects.get_or_create(sp=instance, end_at=None, **contact)
            if created:
                modified = True
                logger.info("Contact added for {service} by {user}"
                            .format(service=instance, user=user))
            removed_contacts = removed_contacts.exclude(pk=contact_instance.pk)
        if removed_contacts:
            modified = True
            for contact in removed_contacts:
                contact.end_at = timezone.now()
                contact.save()
                logger.info("Contact removed from {service} by {user}"
                            .format(service=contact.sp, user=user))
    return modified


def _update_endpoints(validated_data, instance, user, modified):
    if 'endpoints' in validated_data:
        endpoints = validated_data.pop('endpoints')
        removed_endpoints = instance.endpoints.filter(end_at=None)
        for endpoint in endpoints:
            endpoint_instance, created = Endpoint.objects.get_or_create(sp=instance, end_at=None, **endpoint)
            if created:
                modified = True
                logger.info("Endpoint added for {service} by {user}"
                            .format(service=instance, user=user))
            removed_endpoints = removed_endpoints.exclude(pk=endpoint_instance.pk)
        if removed_endpoints:
            modified = True
            for endpoint in removed_endpoints:
                endpoint.end_at = timezone.now()
                endpoint.save()
                logger.info("Endpoint removed from {service} by {user}"
                            .format(service=endpoint.sp, user=user))
    return modified


def _update_redirecturis(validated_data, instance, user, modified):
    if 'redirecturis' in validated_data:
        redirecturis = validated_data.pop('redirecturis')
        removed_redirecturis = instance.redirecturis.filter(end_at=None)
        for redirecturi in redirecturis:
            redirecturi_instance, created = RedirectUri.objects.get_or_create(sp=instance, end_at=None, **redirecturi)
            if created:
                modified = True
                logger.info("RedirectUri added for {service} by {user}"
                            .format(service=instance, user=user))
            removed_redirecturis = removed_redirecturis.exclude(pk=redirecturi_instance.pk)
        if removed_redirecturis:
            modified = True
            for redirecturi in removed_redirecturis:
                redirecturi.end_at = timezone.now()
                redirecturi.save()
                logger.info("RedirectUri removed from {service} by {user}"
                            .format(service=redirecturi.sp, user=user))
    return modified


def _update_usergroups(validated_data, instance, user, modified):
    if 'usergroups' in validated_data:
        usergroups = validated_data.pop('usergroups')
        removed_usergroups = instance.usergroups.filter(end_at=None)
        for usergroup in usergroups:
            usergroup_instance, created = UserGroup.objects.get_or_create(sp=instance, end_at=None, **usergroup)
            if created:
                modified = True
                logger.info("UserGroup added for {service} by {user}"
                            .format(service=instance, user=user))
            removed_usergroups = removed_usergroups.exclude(pk=usergroup_instance.pk)
        if removed_usergroups:
            modified = True
            for usergroup in removed_usergroups:
                usergroup.end_at = timezone.now()
                usergroup.save()
                logger.info("UserGroup removed from {service} by {user}"
                            .format(service=usergroup.sp, user=user))
    return modified


class SPAttributeSerializer(serializers.ModelSerializer):
    attribute = serializers.SlugRelatedField(
        slug_field='friendlyname',
        queryset=Attribute.objects.all()
    )

    class Meta:
        model = SPAttribute
        fields = ('id', 'sp', 'attribute', 'reason', 'oidc_userinfo', 'oidc_id_token', 'validated', 'created_at',
                  'updated_at', 'status')
        read_only_fields = ['validated', 'created_at', 'updated_at', 'status']


class SamlSPAttributeLimitedSerializer(SPAttributeSerializer):
    class Meta:
        model = SPAttribute
        list_serializer_class = ActiveListSerializer
        fields = ('id', 'attribute', 'reason', 'status')
        read_only_fields = ['status']


class SamlServiceProviderSerializer(serializers.ModelSerializer):
    attributes = SamlSPAttributeLimitedSerializer(source='spattribute_set',
                                                  many=True,
                                                  required=False)

    certificates = CertificateLimitedSerializer(many=True, required=False)

    contacts = ContactLimitedSerializer(many=True, required=False)

    endpoints = EndpointLimitedSerializer(many=True, required=False)

    admins = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all(),
        required=False
    )
    admin_groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        required=False
    )

    nameidformat = serializers.SlugRelatedField(
        many=True,
        slug_field='nameidformat',
        queryset=NameIDFormat.objects.filter(public=True),
        required=False
    )

    class Meta:
        model = ServiceProvider
        fields = ['id'] + get_field_names(['basic', 'saml', 'basic_linked', 'saml_linked', 'meta'])
        read_only_fields = get_field_names('meta')
        validators = [
            UniqueTogetherValidator(
                queryset=ServiceProvider.objects.filter(end_at=None),
                fields=['entity_id']
            )
        ]

    def _get_value(self, data, field):
        if field in data:
            return data[field]
        elif self.instance:
            return getattr(self.instance, field, None)
        return None

    def validate_certificates(self, value):
        for instance in value:
            certificate = instance['certificate'] if 'certificate' in instance else None
            signing = instance['signing'] if 'signing' in instance else False
            encryption = instance['encryption'] if 'encryption' in instance else False
            if not signing and not encryption:
                signing = True
                encryption = True
            certificate_validator(None, certificate, signing, encryption, serializers.ValidationError)
        return value

    def validate_endpoints(self, value):
        for instance in value:
            binding = instance['binding'] if 'binding' in instance else None
            index = instance['index'] if 'index' in instance else None
            is_default = instance['is_default'] if 'is_default' in instance else None
            location = instance['location'] if 'location' in instance else None
            endpoint_type = instance['type'] if 'type' in instance else None
            endpoint_validator(self.instance, binding, index, is_default, location, endpoint_type,
                               serializers.ValidationError)
        return value

    def validate(self, data):
        user = self.context['request'].user
        name_en = self._get_value(data, 'name_en')
        name_fi = self._get_value(data, 'name_fi')
        if not name_en and not name_fi:
            raise serializers.ValidationError(_("Name in English or in Finnish is required."))
        if 'entity_id' in data and not user.is_superuser and ":" not in data['entity_id']:
            raise serializers.ValidationError(_("Entity Id should be URI, please contact IdP admins if "
                                                "this is not possible."))
        if 'production' in data and data['production'] and not user.is_superuser:
            missing = get_missing_sp_data(self.instance)
            if missing:
                warning = _('Following parameters are missing for production use: ')
                self.fields['production'].help_text += '<div class="text-danger">' + str(warning) + '<br>' + str(
                    '<br>'.join(missing)) + '</div>'
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        admins = validated_data.pop('admins', None)
        admin_groups = validated_data.pop('admin_groups', None)
        attributes = validated_data.pop('spattribute_set', None)
        certificates = validated_data.pop('certificates', None)
        contacts = validated_data.pop('contacts', None)
        endpoints = validated_data.pop('endpoints', None)
        nameidformat = validated_data.pop('nameidformat', None)

        sp = ServiceProvider.objects.create(service_type='saml', **validated_data)
        if admins:
            sp.admins.set(admins)
        if admin_groups:
            sp.admin_groups.set(admin_groups)
        if nameidformat:
            sp.nameidformat.set(nameidformat)
        # Add user as admin if user is not superuser
        if not user.is_superuser and (not admin_groups or not user.groups.filter(name__in=admin_groups).exists()):
            sp.admins.add(user)
        logger.info("Service {service} created by {user}"
                    .format(service=sp, user=user))
        if attributes:
            for attribute in attributes:
                spattribute = SPAttribute.objects.create(sp=sp, **attribute)
                logger.info("Attribute {attribute} requested for {sp} by {user}"
                            .format(attribute=spattribute.attribute, sp=sp, user=user))
        if certificates:
            for certificate in certificates:
                Certificate.objects.create(sp=sp, **certificate)
                logger.info("Certificate added for {service} by {user}".format(service=sp, user=user))
        if contacts:
            for contact in contacts:
                Contact.objects.create(sp=sp, **contact)
                logger.info("Contact added for {service} by {user}".format(service=sp, user=user))
        if endpoints:
            for endpoint in endpoints:
                Endpoint.objects.create(sp=sp, **endpoint)
                logger.info("Endpoint added for {service} by {user}".format(service=sp, user=user))
        return sp

    def update(self, instance, validated_data):
        changed_data = []
        modified = False
        user = self.context['request'].user
        modified = _update_spattributes(validated_data, instance, user, modified)
        modified = _update_certificates(validated_data, instance, user, modified)
        modified = _update_contacts(validated_data, instance, user, modified)
        modified = _update_endpoints(validated_data, instance, user, modified)

        for field in validated_data:
            if getattr(instance, field) != validated_data[field]:
                changed_data.append(field)

        if changed_data:
            if instance.validated:
                create_sp_history_copy(instance.pk)
            instance.validated = None
            modified = True

        for field in changed_data:
            if field == 'admins':
                instance.admins.set(validated_data[field])
            elif field == 'admin_groups':
                instance.admin_groups.set(validated_data[field])
            elif field == 'nameidformat':
                instance.nameidformat.set(validated_data[field])
            else:
                setattr(instance, field, validated_data[field])

        if changed_data or modified:
            instance.updated_by = user
            logger.info("Service {service} updated by {user}"
                        .format(service=instance, user=user))
            if modified:
                instance.save_modified()
            else:
                instance.save()
        return instance


class OidcSPAttributeLimitedSerializer(SPAttributeSerializer):
    class Meta:
        model = SPAttribute
        list_serializer_class = ActiveListSerializer
        fields = ('id', 'attribute', 'oidc_userinfo', 'oidc_id_token', 'reason', 'status')
        read_only_fields = ['status']


class OidcServiceProviderSerializer(serializers.ModelSerializer):
    attributes = OidcSPAttributeLimitedSerializer(source='spattribute_set',
                                                  many=True,
                                                  required=False)

    contacts = ContactLimitedSerializer(many=True, required=False)

    redirecturis = RedirectUriLimitedSerializer(many=True, required=False)

    admins = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all(),
        required=False
    )
    admin_groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        required=False
    )

    grant_types = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=GrantType.objects.all(),
        required=False
    )

    oidc_scopes = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=OIDCScope.objects.all(),
        required=False
    )

    response_types = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=ResponseType.objects.all(),
        required=False
    )

    class Meta:
        model = ServiceProvider
        fields = ['id'] + get_field_names(['basic', 'oidc', 'basic_linked', 'oidc_linked', 'meta'])
        read_only_fields = get_field_names('meta')
        validators = [
            UniqueTogetherValidator(
                queryset=ServiceProvider.objects.filter(end_at=None),
                fields=['entity_id']
            )
        ]

    def _get_value(self, data, field):
        if field in data:
            return data[field]
        elif self.instance:
            return getattr(self.instance, field, None)
        return None

    def validate_entity_id(self, value):
        test = re.compile("^[a-zA-Z0-9.]+$")
        if not test.match(value):
            raise serializers.ValidationError(_("Only letters, numbers and a dot allowed."))
        return value

    def validate_redirecturis(self, value):
        for instance in value:
            uri = instance['uri'] if 'uri' in instance else None
            redirecturi_validator(self.instance, uri, serializers.ValidationError)
        return value

    def validate(self, data):
        user = self.context['request'].user
        name_en = self._get_value(data, 'name_en')
        name_fi = self._get_value(data, 'name_fi')
        if not name_en and not name_fi:
            raise serializers.ValidationError(_("Name in English or in Finnish is required."))
        if 'production' in data and data['production'] and not user.is_superuser:
            missing = get_missing_sp_data(self.instance)
            if missing:
                warning = _('Following parameters are missing for production use: ')
                self.fields['production'].help_text += '<div class="text-danger">' + str(warning) + '<br>' + str(
                    '<br>'.join(missing)) + '</div>'
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        admins = validated_data.pop('admins', None)
        admin_groups = validated_data.pop('admin_groups', None)
        attributes = validated_data.pop('spattribute_set', None)
        contacts = validated_data.pop('contacts', None)
        grant_types = validated_data.pop('grant_types', None)
        oidc_scopes = validated_data.pop('oidc_scopes', None)
        response_types = validated_data.pop('response_types', None)
        redirecturis = validated_data.pop('redirecturis', None)

        sp = ServiceProvider.objects.create(service_type='oidc', **validated_data)
        if admins:
            sp.admins.set(admins)
        if admin_groups:
            sp.admin_groups.set(admin_groups)
        if grant_types:
            sp.grant_types.set(grant_types)
        if oidc_scopes:
            sp.oidc_scopes.set(oidc_scopes)
        if response_types:
            sp.response_types.set(response_types)
        # Add user as admin if user is not superuser
        if not user.is_superuser and (not admin_groups or not user.groups.filter(name__in=admin_groups).exists()):
            sp.admins.add(user)
        logger.info("Service {service} created by {user}"
                    .format(service=sp, user=user))
        if attributes:
            for attribute in attributes:
                spattribute = SPAttribute.objects.create(sp=sp, **attribute)
                logger.info("Attribute {attribute} requested for {sp} by {user}"
                            .format(attribute=spattribute.attribute, sp=sp, user=user))
        if contacts:
            for contact in contacts:
                Contact.objects.create(sp=sp, **contact)
                logger.info("Contact added for {service} by {user}".format(service=sp, user=user))
        if redirecturis:
            for redirecturi in redirecturis:
                RedirectUri.objects.create(sp=sp, **redirecturi)
                logger.info("RedirectUri added for {service} by {user}".format(service=sp, user=user))
        return sp

    def update(self, instance, validated_data):
        changed_data = []
        modified = False
        user = self.context['request'].user
        modified = _update_spattributes(validated_data, instance, user, modified)
        modified = _update_contacts(validated_data, instance, user, modified)
        modified = _update_redirecturis(validated_data, instance, user, modified)

        for field in validated_data:
            if getattr(instance, field) != validated_data[field]:
                changed_data.append(field)

        if changed_data:
            if instance.validated:
                create_sp_history_copy(instance.pk)
            instance.validated = None
            modified = True

        for field in changed_data:
            if field == 'admins':
                instance.admins.set(validated_data[field])
            elif field == 'admin_groups':
                instance.admin_groups.set(validated_data[field])
            elif field == 'grant_types':
                instance.grant_types.set(validated_data[field])
            elif field == 'oidc_scopes':
                instance.oidc_scopes.set(validated_data[field])
            elif field == 'response_types':
                instance.response_types.set(validated_data[field])
            else:
                setattr(instance, field, validated_data[field])

        if changed_data or modified:
            instance.updated_by = user
            logger.info("Service {service} updated by {user}"
                        .format(service=instance, user=user))
            if modified:
                instance.save_modified()
            else:
                instance.save()
        return instance


class LdapSPAttributeLimitedSerializer(SPAttributeSerializer):
    class Meta:
        model = SPAttribute
        list_serializer_class = ActiveListSerializer
        fields = ('id', 'attribute', 'reason', 'status')
        read_only_fields = ['status']


class LdapServiceProviderSerializer(serializers.ModelSerializer):
    attributes = LdapSPAttributeLimitedSerializer(source='spattribute_set',
                                                  many=True,
                                                  required=False)

    contacts = ContactLimitedSerializer(many=True, required=False)

    admins = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all(),
        required=False
    )
    admin_groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        required=False
    )

    usergroups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=UserGroup.objects.all(),
        required=False
    )

    class Meta:
        model = ServiceProvider
        fields = ['id'] + get_field_names(['basic', 'ldap', 'basic_linked', 'ldap_linked', 'meta'])
        read_only_fields = get_field_names('meta')

    def _get_value(self, data, field):
        if field in data:
            return data[field]
        elif self.instance:
            return getattr(self.instance, field, None)
        return None

    def validate_server_names(self, value):
        server_names_validator(value, serializers.ValidationError)
        return value

    def validate_usergroups(self, value):
        for instance in value:
            name = instance['name'] if 'name' in instance else None
            if UserGroup.objects.filter(sp=self.instance, name=name, end_at=None).exists():
                raise serializers.ValidationError(_("Group already added"))
        return value

    def validate(self, data):
        user = self.context['request'].user
        name_fi = self._get_value(data, 'name_fi')
        if not name_fi:
            raise serializers.ValidationError(_("Finnish name is required."))
        if 'production' in data and data['production'] and not user.is_superuser:
            missing = get_missing_sp_data(self.instance)
            if missing:
                warning = _('Following parameters are missing for production use: ')
                self.fields['production'].help_text += '<div class="text-danger">' + str(warning) + '<br>' + str(
                    '<br>'.join(missing)) + '</div>'
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        admins = validated_data.pop('admins', None)
        admin_groups = validated_data.pop('admin_groups', None)
        attributes = validated_data.pop('spattribute_set', None)
        contacts = validated_data.pop('contacts', None)
        usergroups = validated_data.pop('usergroups', None)
        name_fi = validated_data['name_fi']
        entity_id = new_ldap_entity_id_from_name(name_fi)
        sp = ServiceProvider.objects.create(service_type='ldap', entity_id=entity_id, **validated_data)
        if admins:
            sp.admins.set(admins)
        if admin_groups:
            sp.admin_groups.set(admin_groups)
        # Add user as admin if user is not superuser
        if not user.is_superuser and (not admin_groups or not user.groups.filter(name__in=admin_groups).exists()):
            sp.admins.add(user)
        logger.info("Service {service} created by {user}"
                    .format(service=sp, user=user))
        if attributes:
            for attribute in attributes:
                spattribute = SPAttribute.objects.create(sp=sp, **attribute)
                logger.info("Attribute {attribute} requested for {sp} by {user}"
                            .format(attribute=spattribute.attribute, sp=sp, user=user))
        if contacts:
            for contact in contacts:
                Contact.objects.create(sp=sp, **contact)
                logger.info("Contact added for {service} by {user}".format(service=sp, user=user))
        if usergroups:
            for usergroup in usergroups:
                UserGroup.objects.create(sp=sp, **usergroup)
                logger.info("UserGroup added for {service} by {user}".format(service=sp, user=user))
        return sp

    def update(self, instance, validated_data):
        changed_data = []
        modified = False
        user = self.context['request'].user
        _update_spattributes(validated_data, instance, user, modified)
        _update_contacts(validated_data, instance, user, modified)
        _update_redirecturis(validated_data, instance, user, modified)

        for field in validated_data:
            if getattr(instance, field) != validated_data[field]:
                changed_data.append(field)

        if changed_data:
            if instance.validated:
                create_sp_history_copy(instance.pk)
            instance.validated = None
            modified = True

        for field in changed_data:
            if field == 'admins':
                instance.admins.set(validated_data[field])
            elif field == 'admin_groups':
                instance.admin_groups.set(validated_data[field])
            else:
                setattr(instance, field, validated_data[field])

        if changed_data or modified:
            instance.updated_by = user
            logger.info("Service {service} updated by {user}"
                        .format(service=instance, user=user))
            if modified:
                instance.save_modified()
            else:
                instance.save()
        return instance
