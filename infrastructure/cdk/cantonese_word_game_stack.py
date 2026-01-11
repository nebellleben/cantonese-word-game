"""
AWS CDK Stack for Cantonese Word Game
"""
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_rds as rds,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    Duration,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class CantoneseWordGameStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Configuration
        vpc_cidr = self.node.try_get_context("vpc_cidr") or "10.0.0.0/16"
        db_instance_type = self.node.try_get_context("db_instance_type") or "db.t3.micro"
        frontend_cpu = int(self.node.try_get_context("frontend_cpu") or "256")
        frontend_memory = int(self.node.try_get_context("frontend_memory") or "512")
        backend_cpu = int(self.node.try_get_context("backend_cpu") or "512")
        backend_memory = int(self.node.try_get_context("backend_memory") or "1024")
        desired_count = int(self.node.try_get_context("desired_count") or 2)

        # Create VPC
        vpc = ec2.Vpc(
            self,
            "VPC",
            cidr=vpc_cidr,
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    name="Private",
                    cidr_mask=24,
                ),
            ],
        )

        # Use existing ECR Repositories (they were created manually)
        frontend_repo = ecr.Repository.from_repository_name(
            self,
            "FrontendRepository",
            repository_name="cantonese-word-game-frontend",
        )

        backend_repo = ecr.Repository.from_repository_name(
            self,
            "BackendRepository",
            repository_name="cantonese-word-game-backend",
        )

        # Create Secrets Manager secret for application secrets
        app_secret = secretsmanager.Secret(
            self,
            "AppSecrets",
            secret_name="cantonese-word-game-secrets",
            description="Secrets for Cantonese Word Game application",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"SECRET_KEY":""}',
                generate_string_key="SECRET_KEY",
                exclude_characters='"@/\\',
            ),
        )

        # Create RDS Subnet Group
        db_subnet_group = rds.SubnetGroup(
            self,
            "DBSubnetGroup",
            vpc=vpc,
            description="Subnet group for RDS PostgreSQL",
            subnet_group_name="cantonese-db-subnet-group",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        )

        # Create RDS Security Group
        db_security_group = ec2.SecurityGroup(
            self,
            "DBSecurityGroup",
            vpc=vpc,
            description="Security group for RDS PostgreSQL",
            allow_all_outbound=False,
        )

        # Create RDS PostgreSQL Instance
        db_instance = rds.DatabaseInstance(
            self,
            "PostgreSQLInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            subnet_group=db_subnet_group,
            security_groups=[db_security_group],
            database_name="cantonese_game",
            credentials=rds.Credentials.from_generated_secret(
                "postgres_admin", exclude_characters='"@/\\'
            ),
            allocated_storage=20,
            max_allocated_storage=100,
            backup_retention=Duration.days(1),  # Reduced for free tier compatibility
            deletion_protection=False,
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
            multi_az=False,  # Set to True for production
        )

        # Create ECS Cluster
        cluster = ecs.Cluster(
            self,
            "Cluster",
            cluster_name="cantonese-word-game-cluster",
            vpc=vpc,
        )

        # Create ECS Task Execution Role
        task_execution_role = iam.Role(
            self,
            "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )

        # Grant secrets access to task execution role
        app_secret.grant_read(task_execution_role)

        # Create ECS Task Role for backend
        backend_task_role = iam.Role(
            self,
            "BackendTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # Grant secrets access to backend task role
        app_secret.grant_read(backend_task_role)

        # Create CloudWatch Log Groups
        frontend_log_group = logs.LogGroup(
            self,
            "FrontendLogGroup",
            log_group_name="/ecs/cantonese-word-game-frontend",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        backend_log_group = logs.LogGroup(
            self,
            "BackendLogGroup",
            log_group_name="/ecs/cantonese-word-game-backend",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create Backend Security Group
        backend_security_group = ec2.SecurityGroup(
            self,
            "BackendSecurityGroup",
            vpc=vpc,
            description="Security group for backend service",
            allow_all_outbound=True,
        )

        # Allow backend to access RDS
        db_security_group.add_ingress_rule(
            backend_security_group,
            ec2.Port.tcp(5432),
            "Allow backend to access RDS",
        )

        # Create Backend Task Definition
        backend_task_definition = ecs.FargateTaskDefinition(
            self,
            "BackendTaskDefinition",
            cpu=backend_cpu,
            memory_limit_mib=backend_memory,
            ephemeral_storage_gib=30,  # Increased from default 20GB for large ML dependencies
            execution_role=task_execution_role,
            task_role=backend_task_role,
        )

        # Add backend container
        backend_container = backend_task_definition.add_container(
            "BackendContainer",
            image=ecs.ContainerImage.from_ecr_repository(backend_repo, "latest"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="backend",
                log_group=backend_log_group,
            ),
            environment={
                "API_V1_PREFIX": "/api",
                "PROJECT_NAME": "Cantonese Word Game API",
                "ALGORITHM": "HS256",
                "ACCESS_TOKEN_EXPIRE_MINUTES": "1440",
                # CORS origins - must match frontend origin exactly when using credentials
                "CORS_ORIGINS": "http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com",
            },
            secrets={
                "SECRET_KEY": ecs.Secret.from_secrets_manager(
                    app_secret, "SECRET_KEY"
                ),
                "DATABASE_URL": ecs.Secret.from_secrets_manager(
                    db_instance.secret, "uri"
                ),
            },
        )

        backend_container.add_port_mappings(
            ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP)
        )

        # Create Application Load Balancer (moved here so frontend can reference it)
        alb = elbv2.ApplicationLoadBalancer(
            self,
            "ALB",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="cantonese-word-game-alb",
        )

        # Store ALB DNS in SSM Parameter Store for easy access
        ssm.StringParameter(
            self,
            "ALBDNSParameter",
            parameter_name="/cantonese-word-game/alb-dns",
            string_value=alb.load_balancer_dns_name,
            description="ALB DNS name for Cantonese Word Game"
        )

        # Create Frontend Security Group
        frontend_security_group = ec2.SecurityGroup(
            self,
            "FrontendSecurityGroup",
            vpc=vpc,
            description="Security group for frontend service",
            allow_all_outbound=True,
        )

        # Create Frontend Task Definition
        frontend_task_definition = ecs.FargateTaskDefinition(
            self,
            "FrontendTaskDefinition",
            cpu=frontend_cpu,
            memory_limit_mib=frontend_memory,
            execution_role=task_execution_role,
        )

        # Add frontend container
        frontend_container = frontend_task_definition.add_container(
            "FrontendContainer",
            image=ecs.ContainerImage.from_ecr_repository(frontend_repo, "latest"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="frontend",
                log_group=frontend_log_group,
            ),
            environment={
                "VITE_API_BASE_URL": f"http://{alb.load_balancer_dns_name}:8000/api",
            },
        )

        frontend_container.add_port_mappings(
            ecs.PortMapping(container_port=80, protocol=ecs.Protocol.TCP)
        )

        # Create Backend Target Group
        backend_target_group = elbv2.ApplicationTargetGroup(
            self,
            "BackendTargetGroup",
            vpc=vpc,
            port=8000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path="/health",
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
            ),
        )

        # Create Frontend Target Group
        frontend_target_group = elbv2.ApplicationTargetGroup(
            self,
            "FrontendTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path="/health",
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
            ),
        )

        # Create Backend Listener
        backend_listener = alb.add_listener(
            "BackendListener",
            port=8000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[backend_target_group],
        )

        # Create Frontend Listener
        frontend_listener = alb.add_listener(
            "FrontendListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[frontend_target_group],
        )

        # Allow ALB to access backend
        backend_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(8000),
            "Allow ALB to access backend",
        )

        # Allow internet to access frontend
        frontend_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow internet to access frontend",
        )

        # Create Backend ECS Service
        backend_service = ecs.FargateService(
            self,
            "BackendService",
            cluster=cluster,
            task_definition=backend_task_definition,
            desired_count=desired_count,
            service_name="cantonese-word-game-backend-service",
            security_groups=[backend_security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            health_check_grace_period=Duration.seconds(120),  # Increased for slower startup
        )

        backend_service.attach_to_application_target_group(backend_target_group)

        # Create Frontend ECS Service
        frontend_service = ecs.FargateService(
            self,
            "FrontendService",
            cluster=cluster,
            task_definition=frontend_task_definition,
            desired_count=desired_count,
            service_name="cantonese-word-game-frontend-service",
            security_groups=[frontend_security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            health_check_grace_period=Duration.seconds(90),  # Increased for slower startup
        )

        frontend_service.attach_to_application_target_group(frontend_target_group)

        # CloudWatch Monitoring
        # Create SNS topic for alarms (optional - uncomment to enable email notifications)
        # alarm_topic = sns.Topic(
        #     self,
        #     "AlarmTopic",
        #     topic_name="cantonese-word-game-alarms",
        # )
        # alarm_action = cw_actions.SnsAction(alarm_topic)

        # Backend service alarms
        backend_cpu_alarm = cloudwatch.Alarm(
            self,
            "BackendCPUAlarm",
            metric=backend_service.metric_cpu_utilization(),
            threshold=80,
            evaluation_periods=2,
            alarm_description="Alert when backend CPU utilization exceeds 80%",
        )

        backend_memory_alarm = cloudwatch.Alarm(
            self,
            "BackendMemoryAlarm",
            metric=backend_service.metric_memory_utilization(),
            threshold=80,
            evaluation_periods=2,
            alarm_description="Alert when backend memory utilization exceeds 80%",
        )

        # Frontend service alarms
        frontend_cpu_alarm = cloudwatch.Alarm(
            self,
            "FrontendCPUAlarm",
            metric=frontend_service.metric_cpu_utilization(),
            threshold=80,
            evaluation_periods=2,
            alarm_description="Alert when frontend CPU utilization exceeds 80%",
        )

        frontend_memory_alarm = cloudwatch.Alarm(
            self,
            "FrontendMemoryAlarm",
            metric=frontend_service.metric_memory_utilization(),
            threshold=80,
            evaluation_periods=2,
            alarm_description="Alert when frontend memory utilization exceeds 80%",
        )

        # ALB target health alarms
        backend_target_health_alarm = cloudwatch.Alarm(
            self,
            "BackendTargetHealthAlarm",
            metric=backend_target_group.metric_healthy_host_count(),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            alarm_description="Alert when backend target health is unhealthy",
        )

        frontend_target_health_alarm = cloudwatch.Alarm(
            self,
            "FrontendTargetHealthAlarm",
            metric=frontend_target_group.metric_healthy_host_count(),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            alarm_description="Alert when frontend target health is unhealthy",
        )

        # RDS alarms
        rds_cpu_alarm = cloudwatch.Alarm(
            self,
            "RDSCPUAlarm",
            metric=db_instance.metric_cpu_utilization(),
            threshold=80,
            evaluation_periods=2,
            alarm_description="Alert when RDS CPU utilization exceeds 80%",
        )

        rds_connections_alarm = cloudwatch.Alarm(
            self,
            "RDSConnectionsAlarm",
            metric=db_instance.metric_database_connections(),
            threshold=50,
            evaluation_periods=2,
            alarm_description="Alert when RDS connections exceed 50",
        )

        # CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(
            self,
            "MonitoringDashboard",
            dashboard_name="CantoneseWordGame-Dashboard",
        )

        # Add widgets to dashboard
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Backend CPU Utilization",
                left=[backend_service.metric_cpu_utilization()],
            ),
            cloudwatch.GraphWidget(
                title="Backend Memory Utilization",
                left=[backend_service.metric_memory_utilization()],
            ),
            cloudwatch.GraphWidget(
                title="Frontend CPU Utilization",
                left=[frontend_service.metric_cpu_utilization()],
            ),
            cloudwatch.GraphWidget(
                title="Frontend Memory Utilization",
                left=[frontend_service.metric_memory_utilization()],
            ),
            cloudwatch.GraphWidget(
                title="RDS CPU Utilization",
                left=[db_instance.metric_cpu_utilization()],
            ),
            cloudwatch.GraphWidget(
                title="RDS Connections",
                left=[db_instance.metric_database_connections()],
            ),
            cloudwatch.GraphWidget(
                title="ALB Request Count",
                left=[alb.metric_request_count()],
            ),
            cloudwatch.GraphWidget(
                title="ALB Target Response Time",
                left=[backend_target_group.metric_target_response_time()],
            ),
        )

        # Outputs
        CfnOutput(
            self,
            "LoadBalancerDNS",
            value=alb.load_balancer_dns_name,
            description="DNS name of the load balancer",
        )

        CfnOutput(
            self,
            "FrontendECRRepository",
            value=frontend_repo.repository_uri,
            description="ECR repository URI for frontend",
        )

        CfnOutput(
            self,
            "BackendECRRepository",
            value=backend_repo.repository_uri,
            description="ECR repository URI for backend",
        )

        CfnOutput(
            self,
            "DatabaseEndpoint",
            value=db_instance.instance_endpoint.hostname,
            description="RDS PostgreSQL endpoint",
        )

        CfnOutput(
            self,
            "SecretsManagerSecret",
            value=app_secret.secret_arn,
            description="ARN of the secrets manager secret",
        )

        CfnOutput(
            self,
            "CloudWatchDashboard",
            value=f"https://console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name={dashboard.dashboard_name}",
            description="CloudWatch Dashboard URL",
        )

