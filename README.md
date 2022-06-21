# photo-map-viewer

App uses Mapbox to display photos on the world map based on the gps info of those photos. Clicking on a point shows the photo besides the map, provided that the photos are able to be loaded in a local /assets/ folder.

### Requirements
* Requires an /assets/ folder that contains photo images (.jpg, .jpeg, .heic) to display the photos and create the DataFrame with the relevant EXIF metadata to plot them on a map.
* Requires a Mapbox public access token (free to create an account) stored as 'mapbox_token' in the local directory


### Notes
Currently has hardcoded regions for centering on the map (based off of regions for a photo album this was originally used for). These can be modified in the `regions` variable the `dcc.Dropdown(id='dropdown-map-region'`.

.heic images can be read from and plotted on the map, but when clicking on a point that refers to a .heic image, no image will be displayed.


External stylesheet used: https://codepen.io/chriddyp/pen/bWLwgP.css
