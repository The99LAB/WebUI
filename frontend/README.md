# WebUI (quasar-project)

Web UI for managing libvirt based virtual machines

## Install the dependencies

`npm install`

### Start the app in development mode (hot-code reloading, error reporting, etc.)

- Set `SOCKETIO_ENDPOINT` in `quasar.config.js` correctly
- Set `API_ENDPOINT` in `quasar.config.js` correctly
- Run `quasar dev`

### Lint the files

`npm run lint`

### Format the files

`npm run format`

### Build the app for production

- Set `PRODUCTION_BACKEND_PORT` in `quasar.config.js` to the port of the backend
- Run `quasar build`
- Place files from dist/spa into backend/static except index.html
- Place index.html into backend/templates
