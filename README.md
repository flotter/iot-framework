# iot-framework

This project aims to provide a fully functional end-to-end IOT product framework.

The firmware is currently based on Canonical's Ubuntu Server distro, with many
customizations making it more autonomous and suitable as an embedded Linux IOT
field device, with integrated support for Amazon S3 and an EC2 instance running
an MQTT broker, database and dashboard. The framework is build around a product
customer hierarchy which supports multiple customers, customer sites and multiple
devices (endpoints). Each customer site can individually be updated with an OTA
implementation based on Amazon S3. The firmware payload (application) or the
configuration (networking and OTA settings) can be remotely updated. Finally, the
framework provides full log access for devices running in the field.

Contributions welcome!

## Goal

Make IOT product innovation accessable to everyone, by providing a fully functional
end-to-end example system which can be studied and improved over time.

## Current Platform Support List
- Raspberry Pi 3B

## Shortcomings

- Automatic deployment of AWS resources for a new user:

The goal will be to allow someone to clone the repo and supply the framework with
AWS credentials so that automatic setup of S3 and EC2 can be performed.

- Improved Security

Lots of work remain to improve the overall handling of certificates and endpoint
security. The list is too long to go into detail here.
