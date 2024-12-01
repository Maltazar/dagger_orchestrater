from models.terraform import TerraformModule
import dagger

def run_terraform(tf_module: TerraformModule):
    # Prepare the variables for the Terraform command
    var_args = []
    for var in tf_module.vars:
        for key, value in var.items():
            var_args.append(f"-var={key}={value}")
    
    # Initialize Dagger client
    with dagger.Connection() as client:
        terraform_dir = client.git(tf_module.location).directory("/")
        
        container = (
            client.container()
            .from_("hashicorp/terraform:light")
            .with_mounted_directory("/mnt", terraform_dir)
            .with_workdir("/mnt")
            .with_exec(["terraform", "init"])
            .with_exec(["terraform", "plan", "-out=tf.plan"] + var_args)
            .with_exec(["terraform", "apply", "-auto-approve"] + var_args)
        )
        
        # Execute the container
        container.stdout()