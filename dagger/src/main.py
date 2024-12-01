from config.loader import load_yaml
from secrets.handler import handle_secrets
from modules.terraform import run_terraform
from modules.ansible import run_ansible
from modules.helm import run_helm
from modules.kubectl import run_kubectl

def main():
    deploy_play = load_yaml('dagger_deploy.yaml')
    
    handle_secrets(deploy_play.secrets)
    
    for tf_module in deploy_play.terraform:
        run_terraform(tf_module)
    
    for ansible_module in deploy_play.ansible:
        run_ansible(ansible_module)
    
    for helm_module in deploy_play.helm:
        run_helm(helm_module)
    
    for kubectl_module in deploy_play.kubectl:
        run_kubectl(kubectl_module)

if __name__ == "__main__":
    main()