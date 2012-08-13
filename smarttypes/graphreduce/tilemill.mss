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
  marker-fill: lighten(@darkest, 50%);
  [pagerank >= .02] { marker-fill: lighten(@darkest, 40%); }
  [pagerank >= .04] { marker-fill: lighten(@darkest, 30%); }
  [pagerank >= .08] { marker-fill: lighten(@darkest, 20%); }
  [pagerank >= .16] { marker-fill: rgb(187, 148, 117); } 
  [pagerank >= .32] { marker-fill: rgb(147, 129, 118); }
  [pagerank >= .64] { marker-fill: rgb(145, 90, 54); }
}


@zoom_start: 0;
@zoom_stop: 1.5;
@zoom_diff: @zoom_stop - @zoom_start;
@zoom_step: @zoom_diff / 6;

@zoom_0_base: .50;
#users [zoom = 0]{
  marker-width: @zoom_0_base;
  [pagerank >= .02] { marker-width: @zoom_0_base + @zoom_step * 1; }
  [pagerank >= .04] { marker-width: @zoom_0_base + @zoom_step * 2; }
  [pagerank >= .08] { marker-width: @zoom_0_base + @zoom_step * 3; }
  [pagerank >= .16] { marker-width: @zoom_0_base + @zoom_step * 4; }
  [pagerank >= .32] { marker-width: @zoom_0_base + @zoom_step * 5; }
  [pagerank >= .64] { marker-width: @zoom_0_base + @zoom_step * 6; }
}

@zoom_1_base: .70;
#users [zoom = 1]{
  marker-width: @zoom_1_base;
  [pagerank >= .02] { marker-width: @zoom_1_base + @zoom_step * 1; }
  [pagerank >= .04] { marker-width: @zoom_1_base + @zoom_step * 2; }
  [pagerank >= .08] { marker-width: @zoom_1_base + @zoom_step * 3; }
  [pagerank >= .16] { marker-width: @zoom_1_base + @zoom_step * 4; }
  [pagerank >= .32] { marker-width: @zoom_1_base + @zoom_step * 5; }
  [pagerank >= .64] { marker-width: @zoom_1_base + @zoom_step * 6; } 
}

@zoom_2_base: 1.1;
#users [zoom = 2]{
  marker-width: @zoom_2_base;
  [pagerank >= .02] { marker-width: @zoom_2_base + @zoom_step * 1; }
  [pagerank >= .04] { marker-width: @zoom_2_base + @zoom_step * 2; }
  [pagerank >= .08] { marker-width: @zoom_2_base + @zoom_step * 3; }
  [pagerank >= .16] { marker-width: @zoom_2_base + @zoom_step * 4; }
  [pagerank >= .32] { marker-width: @zoom_2_base + @zoom_step * 5; }
  [pagerank >= .64] { marker-width: @zoom_2_base + @zoom_step * 6; }
}

@zoom_3_base: 2;
#users [zoom = 3]{
  marker-width: @zoom_3_base;
  [pagerank >= .02] { marker-width: @zoom_3_base + @zoom_step * 1; }
  [pagerank >= .04] { marker-width: @zoom_3_base + @zoom_step * 2; }
  [pagerank >= .08] { marker-width: @zoom_3_base + @zoom_step * 3; }
  [pagerank >= .16] { marker-width: @zoom_3_base + @zoom_step * 4; }
  [pagerank >= .32] { marker-width: @zoom_3_base + @zoom_step * 5; }
  [pagerank >= .64] { marker-width: @zoom_3_base + @zoom_step * 6; }
}

@zoom_4_base: 4;
#users [zoom = 4]{
  marker-width: @zoom_4_base;
  [pagerank >= .02] { marker-width: @zoom_4_base + @zoom_step * 1; }
  [pagerank >= .04] { marker-width: @zoom_4_base + @zoom_step * 2; }
  [pagerank >= .08] { marker-width: @zoom_4_base + @zoom_step * 3; }
  [pagerank >= .16] { marker-width: @zoom_4_base + @zoom_step * 4; }
  [pagerank >= .32] { marker-width: @zoom_4_base + @zoom_step * 5; }
  [pagerank >= .64] { marker-width: @zoom_4_base + @zoom_step * 6; }
}

@zoom_5_base: 8;
#users [zoom = 5]{
  marker-width: @zoom_5_base;
  [pagerank >= .02] { marker-width: @zoom_5_base + @zoom_step * 1; }
  [pagerank >= .04] { marker-width: @zoom_5_base + @zoom_step * 2; }
  [pagerank >= .08] { marker-width: @zoom_5_base + @zoom_step * 3; }
  [pagerank >= .16] { marker-width: @zoom_5_base + @zoom_step * 4; }
  [pagerank >= .32] { marker-width: @zoom_5_base + @zoom_step * 5; }
  [pagerank >= .64] { marker-width: @zoom_5_base + @zoom_step * 6; }
}

@zoom_6_base: 16;
#users [zoom = 6]{
  marker-width: @zoom_6_base;
  [pagerank >= .02] { marker-width: @zoom_6_base + @zoom_step * 1; }
  [pagerank >= .04] { marker-width: @zoom_6_base + @zoom_step * 2; }
  [pagerank >= .08] { marker-width: @zoom_6_base + @zoom_step * 3; }
  [pagerank >= .16] { marker-width: @zoom_6_base + @zoom_step * 4; }
  [pagerank >= .32] { marker-width: @zoom_6_base + @zoom_step * 5; }
  [pagerank >= .64] { marker-width: @zoom_6_base + @zoom_step * 6; }
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

