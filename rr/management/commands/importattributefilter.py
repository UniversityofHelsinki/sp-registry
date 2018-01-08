from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.attribute import Attribute
from lxml import etree, objectify
from django.utils import timezone
from django.core.management.base import BaseCommand


def attributefilter_parser(filename):
    parser = etree.XMLParser(ns_clean=True, remove_comments=True, remove_blank_text=True)
    tree = etree.parse(filename, parser)
    root = tree.getroot()
    for a in root:
        if etree.QName(a.tag).localname == "AttributeFilterPolicy":
            entityID = a.get("id")
            if not entityID:
                if etree.QName(a[0].tag).localname == "PolicyRequirementRule":
                    entityID = a[0].get("value")
            sp = None
            try:
                sp = ServiceProvider.objects.get(entity_id=entityID, end_at=None)
            except ServiceProvider.DoesNotExist:
                print("ServiceProvider does not exist: " + entityID)
            if sp:
                for b in a:
                    if etree.QName(b.tag).localname == "AttributeRule":
                        attribute_name = b.get("attributeID").rpartition(':')[2]
                        if attribute_name:
                            try:
                                attribute = Attribute.objects.get(friendlyname=attribute_name)
                                if not SPAttribute.objects.filter(sp=sp, attribute=attribute).exists():
                                    SPAttribute.objects.create(sp=sp,
                                                               attribute=attribute,
                                                               reason="initial dump, please give the real reason",
                                                               updated=timezone.now())
                            except Attribute.DoesNotExist:
                                print("Could not add attribute " + attribute_name + " for " + entityID)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    def handle(self, *args, **options):
        for file in options['files']:
            attributefilter_parser(file)
