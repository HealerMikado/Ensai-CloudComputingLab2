#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.instance import Instance, InstanceEbsBlockDevice
from cdktf_cdktf_provider_aws.security_group import SecurityGroup, SecurityGroupIngress, SecurityGroupEgress
from user_data import user_data

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS", region="us-east-1")

        #Pare feu
        sg = SecurityGroup(
                self, "sg-tp",
                ingress=[
                    SecurityGroupIngress(
                        from_port=22,
                        to_port=22,
                        cidr_blocks=["0.0.0.0/0"],
                        protocol="TCP",
                        description="Accept incoming SSH connection"
                    ),
                    SecurityGroupIngress(
                        from_port=80,
                        to_port=80,
                        cidr_blocks=["0.0.0.0/0"],
                        protocol="TCP",
                        description="Accept incoming HTTP connection"
                    )
                ],
                egress=[
                    SecurityGroupEgress(
                        from_port=0,
                        to_port=0,
                        cidr_blocks=["0.0.0.0/0"],
                        protocol="-1",
                        description="allow all egresse connection"
                    )
                ]
            )
        instance = Instance(self, f"compute",
            tags={"Name":"instance TF"},
            ami="ami-080e1f13689e07408", # l'id de l'os. Pas possible de juste mettre ubuntu
            instance_type="t2.micro", # le type de l'instance
            security_groups = [sg.name],
            key_name="vockey",
            user_data_base64=user_data,
            ebs_block_device= [InstanceEbsBlockDevice(
                device_name="/dev/sda1",
                delete_on_termination=True,
                encrypted=False,
                volume_size=20,
                volume_type="gp2"
            ),
            InstanceEbsBlockDevice(
                device_name="/dev/sdb",
                delete_on_termination=True,
                encrypted=False,
                volume_size=100,
                volume_type="gp2"
            )]
        )

        TerraformOutput(
            self, "public_ip",
            value=instance.public_ip,
            )
        



app = App()
MyStack(app, "cloud_commputing")

app.synth()
