(function () {
	window.addEvent("domready", function () {
		$(document.body.parentNode)
			.addClass(Browser.Platform.name)
			.addClass(Browser.Engine.name);
	});
})();


/* unfortunately, the open flash chart requires this
 * function (to fetch the source data for each graph)
 * to be in the global scope */
window["ofcd"] = new Hash();
function open_flash_chart_data(id) {
	return JSON.encode(window["ofcd"][id]);
}

/* a namespace for all of our
 * global functions to hide in */
var Smspoll = {
	"Pie": new Class({
		"initialize": function(into, values) {
			
			/* ofc requires an array of hashes, which is
			 * a bit long-winded and repetitive. rather
			 * than require this format to be passed into
			 * Smspoll.Pie, we'll convert our array of
			 * typles into this madness automatically */
			var ofc_values = [];
			values.each(function(slice) {
				ofc_values.push({
					"label": slice[0],
					"value": slice[1]
				});
			});
			
			
			/* build the configuration array that
			 * open flash chart wants (it's kind of
			 * dirty, presentation all mixed up with
			 * data), and stash it in a global (omfg
			 * teh fail), to be plucked* out later */
			var key = window["ofcd"].getLength()
			window["ofcd"][key] = {
				"elements": [{
					"type": "pie",
					"values": ofc_values,
					"tip": "#val# of #total#<br>#percent#",
					"colours": ["#cc0000", "#00cc00", "#0000cc", "#cccc00", "#cc00cc", "#00cccc"],
					"start-angle": 90,
					"animate": false
				}],
				
				"x_axis": null,
				"y_axis": null
			};;
			
			
			/* create a div to inject the graph
			 * dynamically, to avoid weird gaps
			 * in the page if JS is disabled */
			var container = new Element("div", {
				"class": "graph"
			}).inject(into, "top");
			var size = container.getSize();
			

			/* insert a pretty graph to display the
			 * results. what? flash is an open standard,
			 * even if the IDE isn't. i hope this works
			 * in gnash. not that i have the proprietary
			 * player installed on my laptop or anything */
			var swf = new Swiff("/assets/open-flash-chart.swf", {
				"container": container,
				"width": size.x,
				"height": size.y,
				"vars": {
					"variables": "true",
					"id": key
				}
			});
			
			
			/* when the window is resized (including the text
			 * size, in most browsers), the container might
			 * have been resized in turn, so update the size
			 * of the flash object */
			$(window).addEvent("resize", function() {
				var size = container.getSize();
				swf.object.height = size.y;
				swf.object.width = size.x;
			});
			
			
			return swf;
		}
	})
};
