# website
Website for homeland social.

This repository contains all of the source code and configuration for the homeland social website.

Here you will find:
 - A Django application that serves as the backend API.
 - A vue.js application that serves as the frontend.
 - A sample haproxy container.
 - Certbot container that handles SSL certificates.
 - PowerDNS authoritative primary and secondary dns servers.
 - Pebble to take the place of letsencrypt.org during development and test.
 - A build system that produces docker container images for all of the above.
