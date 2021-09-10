# ☀️ Find The Sun ☀️

### 🚧 Installation Locally

1. Make sure you have Python installed on your system
2. Clone this repository
3. `python3 -m venv venv`
4. `. venv/bin/activate`
5. `pip install -r requirements.txt`
6. `flask run`


### 🖧 Endpoints

`POST /closest-sunny-city`
```javascript
//Request Body
{
    lat: number, // in decimal degrees
    lon: number  // in decimal degrees
}
```

##### ✔️ Example Good Response
```json
{
  "data": {
    "distance": 8.505448997242349,
    "lat": 34.4212,
    "lon": -84.1191,
    "name": "Some City Name",
    "weather": {
      "description": "clear sky",
      "id": 800,
      "main": "Clear"
    }
  },
  "result": "success"
}
```

##### ❌ Example Bad Response
```json
{
    "result": "failure"
}
```

The request body represents the centerpoint of the circular search for cities and their local weather.
In a web app setting, this would typically just be the user's current location, but can also be supplied manually by address converted to latitude + longitude.
It's expected to be in decimal degrees.

### ⚙️ Deployment to DigitalOcean

I decided to check out [Pulumi](https://www.pulumi.com/) for deploying this application, and it was a joy to use.
It's a superset of Terraform that's built into actual staticly-typed languages like Typescript or C#.
You can see the Pulumi stuff in the `/pulumi` folder.

In case it isn't clear from looking at it, you will need two main environment secrets to deploy it to DigitalOcean.
- You need a DigitalOcean token
- You need a [OpenWeather](https://openweathermap.org/) API Key.

You can get the string values and add them to your local Pulumi configuration with the command:
`pulumi config set <name> <value> --secret`

For Example:

`pulumi config set weatherapitoken some-secret-text-goes-here --secret`

I followed an excellent tutorial here:
<https://www.digitalocean.com/community/tutorials/how-to-manage-digitalocean-and-kubernetes-infrastructure-with-pulumi>

and added the stuff I needed (like an environment variable for the API Key) along the way.

The image that is created from the `Dockerfile` can be found here:
<https://hub.docker.com/repository/docker/sesgoe/python-find-the-sun>

I'm not using any kind of CI setup to push this image -- I built it manually locally and pushed it with a simple `docker push` command.

Once you're done setting everything up, it's as simple as `pulumi up` to set up the kubernetes cluster and start serving traffic through an IP/Port.


### Considerations

The nature of this project was partially a time constraint, so I tried to keep the service logic minimal.

Here are the most important things to note:
- I haven't written Python in a decade, so it's very unlikely the Flask code is idiomatic
- I wanted to try Pulumi for the `infra-as-code` deployment and I budgeted a solid 2 hours to get this app deployed, and went over a little bit
- There's a visual component to this API that is separate that needs to get done
- I have a second task that needs to be completed on top of this weather api task. Time constraints limited my error-handling and other edge cases.