FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api .
COPY ./data/ ./data

RUN chmod +x ./dockerfiles/prod/lambda_entry_script.sh
ENTRYPOINT [ "./dockerfiles/prod/lambda_entry_script.sh","main.handler" ]