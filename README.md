# Image Scraper
The [Image Scraper](src/scraper/image_scraper.py) is a service that searches Google
 images for a given query and returns a number of images specified by the user and
 can be used as a standalone service/API.
 The repository as a whole also has an [AWS S3](src/aws/s3_service.py) service that will
 upload your data object (e.g. an image) to a specified S3 bucket. The scrape and upload
 service as a whole is packaged behind a Flask API via HTTP. 
 
 ## Usage
 When running the Flask app locally, a cURL request like the example shown below 
 would scrape the first image from the Google Image search result of 'Labrador Dogs'
 and save it to an S3 Bucket called 'my-dogs' with a key of 'labrador1.jpeg'.
```
curl -X POST -F 'SearchTerm="Labrador Dogs"' -F 'NumberOfImages=1' -F 'Bucket=my-dogs' -F 'Key=labrador1.jpeg' http://localhost:6164/images
```

Naturally, the services using AWS (s3 upload and the Flask App) rely on you having 
an AWS Account and having valid CLI credentials stored in the file `~/.aws/credentials`. 
See https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html for 
details on how to configure this.
