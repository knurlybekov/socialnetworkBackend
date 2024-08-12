import boto3
import click


def get_current_task_definition(client, cluster, service):
    response = client.describe_services(cluster=cluster, services=[service])
    current_task_arn = response["services"][0]["taskDefinition"]
    return client.describe_task_definition(taskDefinition=current_task_arn)


@click.command()
@click.option("--cluster", help="Name of the ECS cluster", required=True)
@click.option("--service", help="Name of the ECS service", required=True)
@click.option("--image", help="Docker image URL for the updated application", required=True)
def deploy(cluster, service, image):
    client = boto3.client("ecs")

    # Fetch the current task definition
    print("Fetching current task definition...")
    response = get_current_task_definition(client, cluster, service)
    container_definition = response["taskDefinition"]["containerDefinitions"][0].copy()

    # Update the container definition with the new image
    container_definition["image"] = image
    print(f"Updated image to: {image}")

    # Register a new task definition
    print("Registering new task definition...")
    response = client.register_task_definition(
        family=response["taskDefinition"]["family"],
        volumes=response["taskDefinition"]["volumes"],
        containerDefinitions=[container_definition],
        cpu="256",  # Modify based on your needs
        memory="512",  # Modify based on your needs
        networkMode="awsvpc",
        requiresCompatibilities=["FARGATE"],
        executionRoleArn="ecs_task_execution_role_prod",
        taskRoleArn="ecs_task_execution_role_prod"
    )
    new_task_arn = response["taskDefinition"]["taskDefinitionArn"]
    print(f"New task definition ARN: {new_task_arn}")

    # Update the service with the new task definition
    print("Updating ECS service with new task definition...")
    client.update_service(
        cluster=cluster, service=service, taskDefinition=new_task_arn,
    )
    print("Service updated!")


if __name__ == "__main__":
    deploy()