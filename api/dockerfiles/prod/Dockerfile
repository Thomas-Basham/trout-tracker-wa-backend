FROM public.ecr.aws/lambda/python:3.12

# Set working directory to the Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy Python files
COPY ./api/index.py .

# Copy the data directory into the task root so Python can import it
COPY ./data ./data

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Lambda handler entry point
CMD [ "index.handler" ]