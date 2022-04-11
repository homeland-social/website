![docker image](https://github.com/homeland-social/website/actions/workflows/docker-image.yml/badge.svg) [![Documentation Status](https://readthedocs.org/projects/homeland-social-website/badge/?version=latest)](https://homeland-social-website.readthedocs.io/en/latest/?badge=latest) ![Docker Pulls](https://img.shields.io/docker/pulls/homelandsocial/website-final) ![Docker Image Version (latest by date)](https://img.shields.io/docker/v/homelandsocial/website-final)
# www.homeland-social.com

Website for [www.homeland-social.com](https://www.homeland-social.com/)

This repository contains all of the source code and configuration for the homeland social website. You can make pull requests here to release new features or fix bugs. You can also use this code or the docker images to run your own copy of this website.

See [full documentation](https://homeland-social-website.readthedocs.io/).

## Architecture

![overview](https://raw.githubusercontent.com/homeland-social/website/master/docs/images/overview.png)

## Using the site

To use the site, simply [register](https://www.homeland-social.com/#/registration) for an account. Once that is done, you need to install the [Homeland console](https://github.com/homeland-social/console/) container in docker.

Vote on [features you would like to see](https://productific.com/@Homelandsocial).

## Run your own site

The easiest way to run your own copy of this site is to utilize the docker images.

An example stack file is located below. 

[https://github.com/homeland-social/deploy/blob/master/docker/homeland-social.yml](https://github.com/homeland-social/deploy/blob/master/docker/homeland-social.yml)

This stack file makes use of the following images, as well as some supporting services such as redis, postgres etc. The Homeland social conduit project also provides a number of images that are integrated with the website.

[https://github.com/homeland-social/conduit/](https://github.com/homeland-social/conduit/)

## Pull requests

Make a pull request in the usual way. Once merged, new docker images will be automatically published. However, deploys to the website are handled in another repository [https://github.com/homeland-social/deploy/](https://github.com/homeland-social/deploy/).

# LICENSE

Copyright 2022 Homeland Social

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.