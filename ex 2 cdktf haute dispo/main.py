#!/usr/bin/env python
from constructs import Construct
from cdktf import App, NamedRemoteWorkspace, TerraformStack, TerraformOutput, RemoteBackend
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.default_vpc import DefaultVpc
from cdktf_cdktf_provider_aws.default_subnet import DefaultSubnet
from cdktf_cdktf_provider_aws.launch_template import LaunchTemplate
from cdktf_cdktf_provider_aws.lb import Lb
from cdktf_cdktf_provider_aws.lb_target_group import LbTargetGroup
from cdktf_cdktf_provider_aws.lb_listener import LbListener, LbListenerDefaultAction
from cdktf_cdktf_provider_aws.autoscaling_attachment import AutoscalingAttachment
from cdktf_cdktf_provider_aws.autoscaling_group import AutoscalingGroup, AutoscalingGroupLaunchTemplate
from cdktf_cdktf_provider_aws.security_group import SecurityGroup, SecurityGroupIngress, SecurityGroupEgress
from user_data import user_data

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS", region="us-east-1")

        default_vpc = DefaultVpc(
            self, "default_vpc"
        )
         
        # Les AZ de us-east-1 sont de la forme us-east-1x 
        # avec x une lettre dans abcdef. Ne permet pas de déployer
        # automatiquement ce code sur une autre région. Le code
        # pour y arriver est vraiment compliqué.
        az_ids = [f"us-east-1{i}" for i in "abcdef"]
        subnets= []
        for i,az_id in enumerate(az_ids):
            subnets.append(DefaultSubnet(
            self, f"default_sub{i}",
            availability_zone=az_id
        ).id)

        security_group = SecurityGroup(
            self, "sg-tp",
            ingress=[
                SecurityGroupIngress(
                    from_port=22,
                    to_port=22,
                    cidr_blocks=["0.0.0.0/0"],
                    protocol="TCP",
                ),
                SecurityGroupIngress(
                    from_port=80,
                    to_port=80,
                    cidr_blocks=["0.0.0.0/0"],
                    protocol="TCP"
                )
            ],
            egress=[
                SecurityGroupEgress(
                    from_port=0,
                    to_port=0,
                    cidr_blocks=["0.0.0.0/0"],
                    protocol="-1"
                )
            ]
            )
        
        # launch_template = LaunchTemplate(
        #     self, "launch template",
        #     image_id= , # l'id de l'os
        #     instance_type= , # le type de l'instance
        #     vpc_security_group_ids =  ,  # une liste des sécurity groups id
        #     key_name="vockey", 
        #     user_data=user_data,
        #     tags={"Name":"template TF"}
        #     )
        
        # # défintion du ASG
        # asg = AutoscalingGroup(
        #     self, "asg",
        #     min_size=, # taille minimum
        #     max_size=4, # taille maximum
        #     desired_capacity=, # taille au debut
        #     launch_template={"id":}, # un dictionnaire avec la clé id et en valeur l'id du launch template
        #     vpc_zone_identifier= , # la liste des subnets
        #     #target_group_arns= #une list avec les arn des target group
        # )

	    # # définiition du load balancer
        # lb = Lb(
        #     self, "lb",
        #     load_balancer_type= ,# le type de load balancer. Ici "application"
        #     security_groups= # une liste des sécurity groups id,
        #     subnets= # la liste des sous réseaux
        # )

	    # # définition du target group du LB
        # target_group=LbTargetGroup(
        #     self, "tg_group",
        #     port=, # le port sur lequel le traffic arrive
        #     protocol= ,  # le protocole écouté
        #     vpc_id= , #l'id du VPC (réseau) dans lequel sera le group. Ici ça sera le default_vpc
        #     target_type="instance" # le type de cible. Cela peut-être ip, instanve, lambda
        # )

	    # # définition du LB listener. C"est lui qui détermine comment le LB fonctionne
        # lb_listener = LbListener(
        #     self, "lb_listener",
        #     load_balancer_arn=, # l'arn (un identifiant amazon différent de l'id) du load balancer
        #     port=, #le port écouté par le LB
        #     protocol=, #le protocole écouté par le LB
        #     default_action= #le type d'action pour transféré les appels. Ici on fera un forward (cf sujet)
        # )





app = App()
MyStack(app, "cloud_commputing")

app.synth()
