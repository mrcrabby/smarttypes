

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

/*-------------------------------------
init
---------------------------------------*/



function init_social_map(reduction_id, reductions_metadata) {

  if (typeof reduction_id == "undefined") return;

  var map = L.map('map', {
      //scrollWheelZoom: false,
  }).setView([0, 0], 2);

  L.tileLayer('/static/tiles/'+reduction_id+'/{z}/{x}/{y}.png', {
      maxZoom: 5,
      noWrap: true
  }).addTo(map);

  load_community_geojson_layer(reduction_id, map);

}

/*-------------------------------------
community_geojson_layer
---------------------------------------*/
var myStyle = {
    //fillColor: "#FFCC33",
    fillColor: "#FFCC33",
    color: "#cccccc",
    weight: 1,
    opacity: 0.0,
    fillOpacity: 0.1
};

function load_community_geojson_layer(reduction_id, map) {
    $.ajax(
    	{type:"GET",
        url:"/social_map/community_features/" + reduction_id,
        cache:false,
        data:{},
        dataType:"json",
        error:function(){},
        success:function(community_features){
            L.geoJson(community_features, {
                style: myStyle,
      			    onEachFeature: oneach_community_feature,
      			    //pointToLayer: point_to_layer,
      			}).addTo(map);
        }
    });
}

function oneach_community_feature(feature, layer) {
  if (feature.properties && feature.properties.popup_content) {

    //bind map popup
    var popup = layer.bindPopup(feature.properties.popup_content);
    $('#community_'+feature.properties.community_id+ ' a.community_link').click(function(){
      popup.openPopup();
      return false;
    });

    //bind sidebar expand
    $('#community_'+feature.properties.community_id+' .community_expand_content').append(
      $(feature.properties.popup_content).find('div.user_list').html());

    //expand button
    $('#community_'+feature.properties.community_id+ ' a.show_all').click(function(){
      $('#community_'+feature.properties.community_id+ ' .community_leader_container').hide();
      $('#community_'+feature.properties.community_id+ ' .community_expand_container').show();
      return false;
    });

    //hide button
    $('#community_'+feature.properties.community_id+ ' a.hide_all').click(function(){
      $('#community_'+feature.properties.community_id+ ' .community_leader_container').show();
      $('#community_'+feature.properties.community_id+ ' .community_expand_container').hide();
      return false;
    });

  }
}


/*-------------------------------------
need this if loading single points
---------------------------------------*/
/*
var geojsonMarkerOptions = {
    //fillColor: "#FFCC33",
    fillColor: "#FFCC33",
    color: "#cccccc",
    weight: 1,
    opacity: 0.2,
    fillOpacity: 0.3
};

function point_to_layer(feature, latlng) {
	community_size = Math.max(0.15 * feature.properties.community_size, 8);
	community_size = Math.min(community_size, 40);
	geojsonMarkerOptions.radius = community_size;
	return L.circleMarker(latlng, geojsonMarkerOptions);
}
*/


/*-------------------------------------
people_geojson_layer
---------------------------------------*/
function highlight_community(community_idx) {

}


/*
if (!Modernizr.svg) alert("Your browsing from a device that does not support SVG.  That's unfortunate!");
*/


