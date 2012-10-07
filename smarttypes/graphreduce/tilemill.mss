Map {
  background-color: #ffffff;
}



@darkest: #606060;
#users {
  marker-line-color: #cccccc;
  marker-line-width: .2;
  marker-line-opacity: .1;
  marker-allow-overlap: true;
  marker-ignore-placement: true;  
  marker-fill: lighten(@darkest, 60%);
  [hybrid_pagerank >= .02] { marker-fill: lighten(@darkest, 50%); }
  [hybrid_pagerank >= .04] { marker-fill: lighten(@darkest, 40%); }
  [hybrid_pagerank >= .08] { marker-fill: lighten(@darkest, 30%); }
  [hybrid_pagerank >= .16] { marker-fill: rgb(187, 148, 117); } 
  [hybrid_pagerank >= .32] { marker-fill: rgb(147, 129, 118); }
  [hybrid_pagerank >= .64] { marker-fill: rgb(145, 90, 54); }
}

//@zoom_base_multiplier: 1.2;
@zoom_base_multiplier: 2.4;



@zoom_0_base: .25 * @zoom_base_multiplier;
#users [zoom = 0]{
  marker-width: @zoom_0_base;
  //[hybrid_pagerank >= .02] { marker-width: @zoom_0_base * 1.1; }
  //[hybrid_pagerank >= .04] { marker-width: @zoom_0_base * 1.2; }
  //[hybrid_pagerank >= .08] { marker-width: @zoom_0_base * 1.4; }
  //[hybrid_pagerank >= .16] { marker-width: @zoom_0_base * 1.8; }
  //[hybrid_pagerank >= .32] { marker-width: @zoom_0_base * 2.6; }
  //[hybrid_pagerank >= .64] { marker-width: @zoom_0_base * 4.2; }
}

@zoom_1_base: .50 * @zoom_base_multiplier;
#users [zoom = 1]{
  marker-width: @zoom_1_base;
  //[hybrid_pagerank >= .02] { marker-width: @zoom_1_base * 1.1; }
  //[hybrid_pagerank >= .04] { marker-width: @zoom_1_base * 1.2; }
  //[hybrid_pagerank >= .08] { marker-width: @zoom_1_base * 1.4; }
  //[hybrid_pagerank >= .16] { marker-width: @zoom_1_base * 1.8; }
  //[hybrid_pagerank >= .32] { marker-width: @zoom_1_base * 2.6; }
  //[hybrid_pagerank >= .64] { marker-width: @zoom_1_base * 4.2; }
}

@zoom_2_base: 1.0 * @zoom_base_multiplier;
#users [zoom = 2]{
  marker-width: @zoom_2_base;
  //[hybrid_pagerank >= .02] { marker-width: @zoom_2_base * 1.1; }
  //[hybrid_pagerank >= .04] { marker-width: @zoom_2_base * 1.2; }
  //[hybrid_pagerank >= .08] { marker-width: @zoom_2_base * 1.4; }
  //[hybrid_pagerank >= .16] { marker-width: @zoom_2_base * 1.8; }
  //[hybrid_pagerank >= .32] { marker-width: @zoom_2_base * 2.6; }
  //[hybrid_pagerank >= .64] { marker-width: @zoom_2_base * 4.2; }
}

@zoom_3_base: 2 * @zoom_base_multiplier;
#users [zoom = 3]{
  marker-width: @zoom_3_base;
  //[hybrid_pagerank >= .02] { marker-width: @zoom_3_base * 1.1; }
  //[hybrid_pagerank >= .04] { marker-width: @zoom_3_base * 1.2; }
  //[hybrid_pagerank >= .08] { marker-width: @zoom_3_base * 1.4; }
  //[hybrid_pagerank >= .16] { marker-width: @zoom_3_base * 1.8; }
  //[hybrid_pagerank >= .32] { marker-width: @zoom_3_base * 2.6; }
  //[hybrid_pagerank >= .64] { marker-width: @zoom_3_base * 4.2; }
}

@zoom_4_base: 4 * @zoom_base_multiplier;
#users [zoom = 4]{
  marker-width: @zoom_4_base;
  //[hybrid_pagerank >= .02] { marker-width: @zoom_4_base * 1.1; }
  //[hybrid_pagerank >= .04] { marker-width: @zoom_4_base * 1.2; }
  //[hybrid_pagerank >= .08] { marker-width: @zoom_4_base * 1.4; }
  //[hybrid_pagerank >= .16] { marker-width: @zoom_4_base * 1.8; }
  //[hybrid_pagerank >= .32] { marker-width: @zoom_4_base * 2.6; }
  //[hybrid_pagerank >= .64] { marker-width: @zoom_4_base * 4.2; }
}

@zoom_5_base: 8 * @zoom_base_multiplier;
#users [zoom = 5]{
  marker-width: @zoom_5_base;
  //[hybrid_pagerank >= .02] { marker-width: @zoom_5_base * 1.1; }
  //[hybrid_pagerank >= .04] { marker-width: @zoom_5_base * 1.2; }
  //[hybrid_pagerank >= .08] { marker-width: @zoom_5_base * 1.4; }
  //[hybrid_pagerank >= .16] { marker-width: @zoom_5_base * 1.8; }
  //[hybrid_pagerank >= .32] { marker-width: @zoom_5_base * 2.6; }
  //[hybrid_pagerank >= .64] { marker-width: @zoom_5_base * 4.2; }
}

@zoom_6_base: 16 * @zoom_base_multiplier;
#users [zoom = 6]{
  marker-width: @zoom_6_base;
  //[hybrid_pagerank >= .02] { marker-width: @zoom_6_base * 1.1; }
  //[hybrid_pagerank >= .04] { marker-width: @zoom_6_base * 1.2; }
  //[hybrid_pagerank >= .08] { marker-width: @zoom_6_base * 1.4; }
  //[hybrid_pagerank >= .16] { marker-width: @zoom_6_base * 1.8; }
  //[hybrid_pagerank >= .32] { marker-width: @zoom_6_base * 2.6; }
  //[hybrid_pagerank >= .64] { marker-width: @zoom_6_base * 4.2; }
}

/*
@community_base_pixels: 10;
#community{
  marker-fill: #FFCC33;
  marker-opacity: .3;
  marker-line-color: #999999;
  marker-line-opacity: .1;
  marker-line-width: 2;
  marker-allow-overlap: true;
  marker-ignore-placement: true;
  [zoom = 0] { marker-width: @community_base_pixels * 1.2;}
  [zoom = 1] { marker-width: @community_base_pixels * 2.0;}
  [zoom = 2] { marker-width: @community_base_pixels * 2.7;}
  [zoom = 3] { marker-width: @community_base_pixels * 3.5;}
  [zoom = 4] { marker-width: @community_base_pixels * 6.4;}
  [zoom = 5] { marker-width: @community_base_pixels * 12.8;}
  [zoom = 6] { marker-width: @community_base_pixels * 25.6}
}
*/

