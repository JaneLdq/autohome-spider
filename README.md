# autohome-spider

## Preparation

### Prepare Python Environment

* Python version: 2.7
* PyV8 is needed, you can use commands below to install PyV8:
```
apt-get install -y libboost-all-dev
git clone https://github.com/buffer/pyv8.git
cd pyv8
python setup.py build
python setup.py install
```
* Install other required packages list in requirements.txt

### Install MongoDB

* Install [MongoDB](https://docs.mongodb.com/manual/introduction/) and update the related settings. Default value for MongoDB in this project shown below:

```
MONGO_URI = 'localhost:27017'
MONGO_DATABASE = 'autohome'
```


### Others

* You will need to create a folder named `fonts` under the root directory, this will be needed when parse detail pages.

## How to run
1. run this command to crawl the remaining series list pages and all the failed detail pages.
```
scrapy crawl new_feedbacks
```
