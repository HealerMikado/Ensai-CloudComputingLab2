# TP 2 - Terraform 🪐 et la création infrastructure avec du code 👩‍💻

## Mise en place

Ouvrez un terminal et créez un dossier `cloud computing` avec la commande `mkdir "cloud computing"`. Déplacez-vous dans le dossier avec la commande `cd "cloud computing"`. Clonez le dépôt git du TP avec un `git clone https://github.com/HealerMikado/Ensai-CloudComputingLab2.git`. Vous y trouverez deux dossiers, `ex 1 cdktf ec2` et `ex 2 cdktf haute dispo`. Le premier sera utilisé pour le premier exercice, et le second pour le second.

## Mon premier script avec le CDK Terraform

### Une instance de base

Ouvrez le fichier `main.py`. Il contient architecture minimal du code nécessaire pour que vous puissiez réaliser le TP

```python
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
        TerraformOutput(
            self, "public_ip",
            value=instance.public_ip,
            )


app = App()
MyStack(app, "cloud_commputing")

app.synth()

```

Les imports sont tous les imports dont vous aurez besoin. Il ne sont pas évident à trouver, donc je vous les donnes.

 La classe `MyStack` va contenir toute votre architecture. Pour associer les services que vous allez créer à votre *stack*, vous allez passer en paramètre la stack courante à tous nos objets. Ainsi **tous les objets AWS que nous allons créer vont avoir en premier argument `self`**. 

Maintenant vous allez définir votre première ressource. La classe du cdktf associée à une instance EC2 d'AWS est la classe `Instance`. Les deux premiers arguments à passer au constructeur de la classe `Instance` sont la stack courante, et un id sous la forme d'une chaîne de caractères.

> 🧙‍♂️ Sauf rare exception, tous les objets que vous allez créez vos avoir comme premiers argument la stack courante et un id.

```python
instance = Instance(
    self, "webservice")
```

Ensuite via des paramètres nommées vous allez définir un peu plus en détail votre instance. Rappelez-vous, pour une instance EC2 il nous faut définir son OS (appelé AMI chez AWS) et le type d'instance.

Ajoutez à votre instance son AMI avec le paramètre `ami` qui prendra comme valeur `ami-04b4f1a9cf54c11d0` (c'est l'identifiant de l'AMI ubuntu dans la région `us-east-1`), et pour le type d'instance vous prendrez une `t2.micro`. Exécutez votre architecture avec la commande `cdktf deploy` dans le terminal. Connectez-vous au dashboard EC2 et vérifiez que votre instance est bien démarrée. Néanmoins si vous essayez de vous connectez en SSH à votre instance vous allez voir que c'est impossible. En effet lors de la définition de l'instance nous n'avons pas définis la clé SSH à utiliser, et le *security group* de l'instance. Tout cela fait que pour le moment l'instance n'est pas accessible.

### Configuration de la partie réseau

Vu que ce n'est pas intéressant à trouver seul, voici le code pour définir le *security group* de l'instance :

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
Ce *security group* n'accepte que les connexions HTTP et SSH en entrée, et permet tout le traffic en sortie. Pour associer ce *security group* à votre instance vous allez devoir ajouter un paramètre `security_groups` lors de la création de l'objet. Attention ce paramètre attend une liste de *security groups*. Pour définir la clé, ajoutez le paramètre `key_name` avec comme valeur le nom de la clé (`vockey`). Vous pouvez maintenant relancer votre instance avec un nouveau `cdktf deploy`. Cela va résilier l'instance précédente et en créer une nouvelle.

### Configuration des user data

Pour le moment nous n'avons pas défini les *user data* de l'instance. Pour les ajouter il faut simplement ajouter le paramètre `user_data_base64` avec comme valeur la variable contenu dans `user_data.py` (la valeur est déjà importée). Relancez votre *stack*, et après quelques instants vous pourrez vous connectez au webservice de l'instance. Utilisez l'ip qui s'affiche dans votre terminal après un `cdktf deploy`

### Configuration du disk (bonus)
Actuellement l'instance créée n'a qu'un disque de 8Go. C'est suffisant mais il est possible changer cela via Terraform. Par exemple ajoutez ce bout de code à votre instance.
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
Le premier disque de l'instance aura ainsi un volume de 20 Go, et un second disque sera attaché avec un volume de 100 Go. Et les deux disques seront supprimés en même temps que l'instance. Vous pouvez voir les deux disques en vous connectant à l'instance en SSH et en exécutant la commande `df` (*disk free*)


## Mise en place d'un Auto Scalling Group et d'un Load Balancer

Ci dessous vous trouverez l'architecture finale que vous allez mettre en place pour ce TP. Elle est un peu plus détaillée que lors du précédent TP pour faire apparaitre chaque élément que vous allez devoir définir. Se détacher de l'interface graphique pour utiliser un outil IaC fait réaliser à quel point l'interface masque de nombreux détails. Tout implémenter n'est pas difficile, mais est laborieux quand on est pas guidé. Toutes les étapes sont découpées pour être unitaire et simple. Elles consistent toutes à définir un objet python avec la bonne classe et les bons paramètres. Ce n'est pas simple à trouver cela seul, alors je vous donne tout. Il suffit de suivre le TP à votre rythme.

<img src="img/Architecuture finale.jpg" style="zoom: 50%;" />



Vous trouverez les code de ces exercices dans le dossier `ex 2 cdktf haute dispo`

### Launch Template

La première étape va être de définir le *template* des instances de l'*Auto Scalling Group*. Pour cela vous allez utiliser la classe `LaunchTemplate`. Comme un *template* est quasiment la même chose qu'une instance, l'objet `LaunchTemplate` va fortement ressembler à une instance, seul les noms des paramètres vont changer (oui il n'y a pas une cohérence sur les noms). Ainsi votre objet `LaunchTemplate` va avoir comme paramètres :
- le stack courante,
- un id sous la forme d'un string
- `image_id` qui va définir son image AMI
- `instance_type` qui va définir le type d'instance
- `user_data` qui va définir les user data. Attention même si ce n'est pas précisé, elles doivent bien être encodées en base 64
- `vpc_security_group_ids` au lieu de security_groups pour la liste des *security groups*
- `key_name` pour la clef SSH à utiliser.

### Auto Scalling Group

Maintenant le *template* défini, c'est le moment de l'utiliser avec un *Auto Scalling Group*. Souvenez vous un *Auto Scalling Group* va maintenir un nombre d'instances compris entre le min et le max défini. La classe qui représente un ASG est simplement `AutoscalingGroup`. Elle prend un paramètre :
- le stack courante,
- un id sous la forme d'un string
- `min_size`, `max_size` et `desired_capacity` pour la limite inf, sup, et la valeur initiale.
- `launch_template` qui permet de spécifier le *template* à utiliser. Vous pouvez passer un dictionnaire contenant uniquement la clef `id` avec comme valeur l'id du *launch template* que vous obtiendrez avec l'attribut `id` du *launch template*.
- `vpc_zone_identifier` permet de spécifier les sous réseaux à utiliser pour l'Auto Scalling Group. Utiliser la variable subnets présente dans le fichier.


Il ne vous reste plus qu'à lancer votre code. Il va créer les sous-réseaux nécessaires, un Launch Template et un ASG selon vos spécification. Attendez quelques instants puis allez sur le dashboard EC2, vous devrez voir apparaitre 3 instances.

### Elastic Load Balancer

Dernière pièce à définir, le *Load Balancer* va avoir la charge de répartir les requêtes entre nos instances. La création via l'interface a caché pas mal de choses et au lieu de créer un simple objet, il faut en créer 3 :
- le *Load Balancer* en tant que tel
- le *Target Group* qui va permettre de considérer l'ASG comme une cible possible pour le *Load Balancer*
- et un *Load Balancer Listener* pour relier les deux.

#### Load Balancer

Définir le *Load Balancer* est assez simple. En plus des classiques stack courante et id il prend en paramètre :
- son type avec le paramètre ``load_balancer_type`. Dans le cas présent cela sera "application"
- les sous-réseaux avec lesquels il communique avec le paramètre `subnets`. Prenez la valeur subnets déjà définie.
- et les groupes de sécurités qui lui sont associés avec le paramètre `security_groups`. Le *security group* déjà défini convient très bien. Attention ce paramètre attend une liste.

#### Target Group

Le Target Group est également facile. En plus de la stack et son id il nous faut définir les paramètres :
- `port` en spécifiant le port 80 et protocole en spécifiant `HTTP` car nous voulons que le TG soit accessible uniquement en HTTP sur le port 80.
- `vpc_id` avec l'id du VPC déjà défini. Cela est nécessaire car permet à AWS de savoir que les machines du *Target Group* seront dans le réseau. 

Il faut maintenant associer votre *Target Group* à votre ASG. Cela passe par l'ajout d'un attribut `target_group_arns` dans l'ASG. Cet attribut attend la liste des arn (Amazon Resource Names) des Target Groups. Votre Target Group expose son arn via l'attribut `arn`.


#### Load Balancer Listener

Il ne nous reste plus à dire au *Load Balancer* de forwarder les requêtes HTTP vers notre *Target Group*. Il faut utiliser l'objet `LbListener` pour ça. Il prend en plus des paramètres habituels : 
- `load_balancer_arn` qui est l'arn du Load Balancer. Pour récupérer l'arn de votre Load Balancer utilisez l'attribut `arn`
- `port` qui va prendre la valeur 80 car nous allons forwarder les requêtes faites sur le port 80
- `protocol` qui va prendre la valeur HTTP car nous allons forwarder les requêtes HTTP
- `default_action` où nous allons dire ce que nous voulons faire, ici forwarder les requêtes vers notre *Target Group*. Comme un *Load Balancer Listener* peut avoir plusieurs actions, ce paramètre attend un liste. Ensuite notre action de forward va se définir avec le via un autre objet dont voici le code`LbListenerDefaultAction(type="forward", target_group_arn=target_group.arn)` 


Vous pouvez maintenant relancer votre code avec un `cdktf deploy`, allez sur la page du load balancer, obtenir son adresse dns et accéder au endpoint `/instance`. Rafraichissez la page et l'id affichez devrait changer régulièrement.

## Conclusion

Vous venez lors de ce TP de créer via du code toute une infrastructure informatique. Même si cela n'est pas simple à faire, le code que vous avez écrit peut être maintenant réutiliser à l'infini et versionner via git. Il est ainsi partageable, et vous pouvez voir son évolution. Il peut également utilisé dans un pipeline de CI/CD pour que architecture soit déployée automatiquement.

Même si les solution IaC ont des avantages, je ne vous les recommandes pas pour découvrir un service. Explorer l'interface dans un premier temps pour voir les options disponibles permet de mieux comprendre le service. Automatisez la création de service via du code par la suite si c'est nécessaire.