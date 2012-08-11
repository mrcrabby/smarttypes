

/*

The map page does 2 things:

- It loads a list of all available reductions (metadata)

- Then it loads a specific reduction

--------------------------

To specify a specific map (reduction):

/reduction_id

or

/root_user_screen_name

--------------------------

To specify a specific community, prefix w/ a 'c':

/reduction_id/c_community_idx

or

/root_user_screen_name/c_community_idx

--------------------------

To specify a specific person, prefix w/ a 'p':

/reduction_id/p_person_id

or

/root_user_screen_name/p_person_id

--------------------------

If no reduction is specified we'll see if the user's logged in

Then finally we'll pick a random or popular reduction

--------------------------

First we load the page (this includes available reductions metadata)

Then we load the reduction via ajax 

Then we zoom to the community or person if specified

*/


function init_social_map(reduction_id, reductions_metadata) {

  if (typeof reduction_id == "undefined") return;

  var map = L.map('map', {
      //scrollWheelZoom: false
  }).setView([0, 0], 2);

  L.tileLayer('http://localhost:9999/static/tiles/'+reduction_id+'/{z}/{x}/{y}.png', {
      maxZoom: 6
  }).addTo(map);

}

function get_reduction_geojson(url) {

}

function highlight_community(community_idx) {

}

function highlight_person(person_id) {

}


/*
if (!Modernizr.svg) alert("Your browsing from a device that does not support SVG.  That's unfortunate!");
*/


