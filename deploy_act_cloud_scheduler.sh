#!/bin/bash
gcloud functions deploy scheduler_controller \
      --source=./scheduler-controller \
      --runtime python37 \
      --trigger-event providers/cloud.firestore/eventTypes/document.write \
      --trigger-resource "projects/example5-237118/databases/(default)/documents/apps/cryptotrader-com/users/sandro/iterations/{year}/{month}/{day}/setups/{exchange}/{pair}/{tradeid}"

