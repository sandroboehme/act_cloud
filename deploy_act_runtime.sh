#!/bin/bash
gcloud functions deploy act \
      --runtime python37 \
      --trigger-topic act_runtime_v1
