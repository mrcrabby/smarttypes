

    <!-- begin Chrome zoom bug workaround

      From http://rklancer.github.com/lab/examples/css-layout/

      Force browser to reparse styles and media queries on all window resize events, including page
      zoom. Works around Chromium bug in which media queries are not re-evaluated on page zoom.
      Adapted from http://alastairc.ac/2012/01/zooming-bug-in-webkit/#comment-129553
    -->
    <style id="dummyStyle"></style>
    <script type="text/javascript">
      window.onresize = function() {
        document.getElementById('dummyStyle').textContent = 'dummySelector {}';
      };
    </script>
    <!-- end Chrome zoom bug workaround -->

    <script type="text/javascript">
      if (!Modernizr.svg) alert("Your browsing from a device that does not support SVG.  That's unfortunate!");
    </script>




var chart = $("#chart"),
    aspect = chart.width() / chart.height(),
    container = chart.parent();
$(window).on("resize", function() {
    var targetWidth = container.width();
    chart.attr("width", targetWidth);
    chart.attr("height", Math.round(targetWidth / aspect));
}).trigger("resize");








