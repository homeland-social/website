from back.celery import task


@task
def add_dns(domain_id):
    pass
