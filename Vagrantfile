# -*- mode: ruby -*-
# vi: set ft=ruby :

class VagrantPlugins::ProviderVirtualBox::Action::Network
  def dhcp_server_matches_config?(dhcp_server, config)
    true
  end
end

Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu2204"

  config.vm.network "forwarded_port", guest: 443, host:8443

  config.vm.provision "shell", inline: "which python3 || sudo apt -y install python3"

  config.vm.provision "ansible" do |ansible|
    ansible.extra_vars = { ansible_python_interpreter:"/usr/bin/python3" }
    ansible.playbook = "ansible/playbook.yml"

    roles_file = 'ansible/requirements.yml'

    if File.exist?(roles_file) && !Psych.load_file(roles_file).equal?(nil)
      ansible.galaxy_role_file = roles_file
      ansible.galaxy_roles_path = '/home/vagrant/.ansible/roles/'
      ansible.galaxy_command = 'ansible-galaxy install --role-file=%{role_file} --roles-path=%{roles_path} --force'
    end
  end
end
