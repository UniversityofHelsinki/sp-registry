# -*- mode: ruby -*-
# vi: set ft=ruby :

class VagrantPlugins::ProviderVirtualBox::Action::Network
  def dhcp_server_matches_config?(dhcp_server, config)
    true
  end
end

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"

  config.vm.network "forwarded_port", guest: 443, host:8443
#  config.vm.network "private_network", :name => 'vboxnet0', :ip => '192.168.56.151'

  config.vm.provision "shell", inline: "which python || sudo apt -y install python"

  config.vm.provision "ansible" do |ansible|
    ansible.verbose = "v"
    ansible.playbook = "ansible/playbook.yml"

    roles_file = 'ansible/requirements.yml'

    if File.exist?(roles_file) && !Psych.load_file(roles_file).equal?(nil)
      ansible.galaxy_role_file = roles_file
      ansible.galaxy_roles_path = '/home/vagrant/.ansible/roles/'
      ansible.galaxy_command = 'ansible-galaxy install --role-file=%{role_file} --roles-path=%{roles_path} --force'
    end
  end
end
