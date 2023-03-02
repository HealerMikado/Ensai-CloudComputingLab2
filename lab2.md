# Lab 2

## Mise en place

## Mon premier script avec le CDK Terraform

### Une instance de base

Ouvrez le fichier `cdktf-basic-ec2.py`. Il contient l'architecure minimal du code nécessaire au fonctionnement du CDK Terraform. La classe `MyStack` va contenir toute votre architecture. Pour associer les services que nous allons créer à notre stack, nous allons passer en paramètre la stack à tous nos objets. Ainsi **tous les objets AWS que nous allons créer vont avoir en premier argument `self`**. 

Maintenant vous allez définir votre première ressource. La classe du cdktf associé à une instance EC2 d'AWS et la classe `Instance`. Les deux premiers arguments à passer au constructeur de la classe `Instance` sont la stack courante, et un id sous la forme d'une chaîne de caractères. 

```python
instance = Instance(
    self, "webservice")
```

Ensuite via des paramètres nommées vous allez définir un peu plus en détail votre instance. Rappellez vous, pour une instance EC2 il nous faut définir son OS (appelé AMI chez AWS) et le type d'instance.

Ajoutez à votre instance son AMI avec le paramètre `ami` qui prendra comme valeur `ami-0557a15b87f6559cf` (c'est l'identifiant de l'AMI ubuntu), et pour le type d'instance vous prendrez une `t2.micro`. Exécutez votre architecture avec la commande `cdktf deploy`. Connectez-vous au dashboard EC2 et vérifiez que votre instance est bien up. Néanmoins si vous essayez de vous connectez en SSH à votre instance vous allez voir que c'est impossible. En effet lors de la définition de l'instance nous n'avons pas définis la clé SSH à utiliser, et le *security group* de l'instance. Tout cela fait que pour le moment l'instance n'est pas accessible. 

### Configuration de la partie réseau

Vu que ce n'est pas intéressant à trouver seul, voici le code pour définir le security group de l'instance :

```python
security_group = SecurityGroup(
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
```
Ce *security group* n'accepte que les connexions HTTP et SSH en entrée, et permet tout le traffic en sortie.
Pour associer ce *security group* à votre instance vous allez devoir ajouter un paramètre `security_groups` lors de la création de l'objet. Attention ce paramètre attend une liste de *security groups*.
Pour définir la clé, ajoutez le paramètre `key_name` avec comme valeur le nom de la clé (vockey).
Vous pouvez maintenant relancer votre instance avec un nouveau `cdktf deploy`. Cela va résilier l'instance précédente et en créer une nouvelle.

### Configuration des user data

Pour le moment nous n'avons pas défini les *user data* de l'instance. Pour les ajouter il faut simplement ajouter le paramètre `user_data_base64` avec comme valeur la variable contenu dans `user_data.py` (faites simplement un import). Relancez votre stack, et après quelques instants vous pourrez vous connectez au webservice de l'instance. Utilisez l'ip qui s'affiche dans votre terminal après un `cdktf deploy`

### Configuration du disk (bonus)
Actuellement l'instance crée à un disque par défaut. Mais il est possible de le configurer  le nombre et la taille des disques. Par exemple ajoutez ce bout de code à votre instance.
```python
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
```
Le premier disque de l'instance aura ainsi un volume de 20 Go, et un second disque sera attaché avec un volume de 100 Go. Et les deux disques seront supprimés en même temps que l'instance.


## Mise en place d'un Auto Scalling Group et d'un Load Balancer

### Launch Template
La première étape va être de définir le template des instances de l'*Auto Scalling Group*. Pour cela vous allez utiliser la classe `LaunchTemplate`. Comme un template est quasiment la même chose qu'une instance, l'objet template va fortement ressembler à une instance, seul les noms des paramètres vont changer (oui il n'y a pas une cohérence sur les noms). Ainsi votre objet `LaunchTemplate` va avoir comme paramètre :
- le stack courante,
- un id sous la forme d'un string
- image_id qui va dééfinir son image AMI
- instance_type qui va dééfinir le type d'instance
- user_dat qui va dééfinir les user data. Attention même si ce n'est pas précisé, elles doivnet bien être encodées en base 64
- vpc_security_group_ids au lieu de security_groups pour la liste des security group
- key_name pour la clef.

### Auto Scalling Group

Maintenant le template défini, c'est le moment de l'utiliser avec un Auto Scalling Group. Souvenez vous un Auto Scalling Group va maintenir un nombre d'instances compris entre le min et le max défini. La classe qui représente un ASG est simplement `AutoscalingGroup`. Elle prend un paramètre :
- le stack courante,
- un id sous la forme d'un string
- min_size, max_size et desired_capacity pour la limite inf, sup, et la valeur initiale.
- launch_template qui permet de spcifier le templater à utiliser. Vous pouvez passer un dictionnaire contenant uniquement la clef `id` et l'id du launche template que vous obtiendrez avec l'attribut `id` du launch template.
- vpc_zone_identifier permet de spécifier les sous réseaux à utiliser pour l'Auto Scalling Group. Utiliser la variable subnets présente dans le fichier.


Il ne vous reste plus qu'à lancer votre code. Il va créer les sous-réseaux nécessaires, un Launch Template et un ASG selon vos spécification. Attendez quelques instants puis allez sur le dashboard EC2, vous devrez voir apparaitre 3 instances.

### Elastic Load Balancer

Dernière pièce à définir, le Load Balancer va avoir la charge de répartir les requêtes entre nos instances. La création via l'interface à caché pas mal de chose et au lieu de créer un simple objet, il faut en créer 3 :
- le Load Balancer en tant que tel
- le Target Group qui va permettre de considérer l'ASG comme une cible possible pour le Load Balancer
- et un Load Balancer Listener pour relier les deux.

#### Créer le Load Balancer

Définir le Load Balancer est assez simple. En plus des classiques stack courante et id il prend en paramètre :
- son type avec le paramètre ``load_balancer_type`. Dans le cas présent cela sera "application"
- les sous-réseaux avec lesquels il communique avec le paramètre `subnets`. Prennez la valeur subnets déjà définie.
- et les groupes de sécurités qui lui sont associés avec le paramètre security_groups. Le sécurity group déjà défini convient très bien.Attention ce paramètre attend une liste.

#### Créer le Target Group

Le Target Group est également facile. En plus de la stack et son id il nous faut définir les paramètres :
- port en spécifiant le port 80 et protocol en spécifiant HTTP car nous voulons que le TG soit accessible uniquement en HTTP sur le port 80.
- vpc_id avec l'id du VPC déjà défini. Cela est nécessaire car permet à AWS de savoir que les machines du Target Group seront dans le réseau. 

Il faut maintenant assocer votre Target Group à votre ASG. Cela passe par l'ajout d'un attribut `target_group_arns` dans l'ASG. Cet attribut attend la liste des arn (Amazon Resource Names) des Target Groups. Votre Target Group expose son arn via l'attribut `arn`.


#### Créer le Load Balancer Listener

Il ne nous reste plus à dire au Load Balancer de forwarder les requêtes HTTP vers notre Target Group. Il faut utiliser l'objet `LbListener` pour ça. Il prend en plus des paramètres habituels : 
- load_balancer_arn qui est l'arn du Load Balancer. Pour récupérer l'arn de votre Load Balancer utilisez l'attribut `arn`
- port qui va prendre la valeur 80 car nous allons forwarder les requêtes faites sur le port 80
- protocol qui va prendre la valeur HTTP car nous allons forwarder les requêtes HTTP
- default_action où nous allons dire ce que nous voulons fair, ici forwarder les requêtes vers notre Target Group. Comme un Load Balancer Listener peut avoir plusieurs actions, ce paramètre attend un liste. Ensuite notre action de forward va se définir avec le via un autre objet dont voici le code`LbListenerDefaultAction(type="forward", target_group_arn=target_group.arn)` 


Vous pouvez maintenant relancer votre code avec un `cdktf deploy`, allez sur la page du load balancer, obtenir son adresse dns et accéder au endpoint `/instance`. Rafraichissez la page et l'id affichez devrait changer régulièrement.

## Conlusion