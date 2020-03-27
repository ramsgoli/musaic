 #!/usr/bin/env bash
aws lambda update-function-code \
	--function-name mosaic_generator \
	--zip-file fileb://~/projects/musaic/lambda/linux-lambda.zip
