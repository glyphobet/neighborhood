// next 4 functions copyright 'free' from quirksmode.org. 
function findPosX(obj)
{
	var curleft = 0;
	if (obj.offsetParent)
	{
		while (obj.offsetParent)
		{
			curleft += obj.offsetLeft
			obj = obj.offsetParent;
		}
	}
	else if (obj.x)
		curleft += obj.x;
	return curleft;
}

function findPosY(obj)
{
	var curtop = 0;
	if (obj.offsetParent)
	{
		while (obj.offsetParent)
		{
			curtop += obj.offsetTop
			obj = obj.offsetParent;
		}
	}
	else if (obj.y)
		curtop += obj.y;
	return curtop;
}

function getVertScroll() {
	var y;
	if (self.pageYOffset) // all except Explorer
	{
		y = self.pageYOffset;
	}
	else if (document.documentElement && document.documentElement.scrollTop)
		// Explorer 6 Strict
	{
		y = document.documentElement.scrollTop;
	}
	else if (document.body) // all other Explorers
	{
		y = document.body.scrollTop;
	}
	return y;
}

function getHorizScroll() {
	var x;
	if (self.pageYOffset) // all except Explorer
	{
		x = self.pageXOffset;
	}
	else if (document.documentElement && document.documentElement.scrollTop)
		// Explorer 6 Strict
	{
		x = document.documentElement.scrollLeft;
	}
	else if (document.body) // all other Explorers
	{
		x = document.body.scrollLeft;
	}
	return x;
}

function ss(w){ window.status=w;return true; }

var showingMap = false;

var w = 844;
var h = 718;

// overlay full size map over half size map
function displayMap(pageX, pageY, clientX, clientY, width, height) {
  if (showingMap) {
    if (document.getElementById) {
      var overlay  = document.getElementById('overDiv');
      var clipWidth  = (width=='')?400:width;
      var clipHeight = (height=='')?400:height;

      var posx = 0;
      var posy = 0;
		
      if (pageX || pageY) {
	posx = pageX;
	posy = pageY;
      } else if (clientX || clientY) {
	posx = clientX + getHorizScroll();
	posy = clientY + getVertScroll();
      }

      var xoverflow = 0;
      var yoverflow = 0;

      if (posx < clipWidth/2){
	xoverflow = posx - clipWidth/2;
      } else if (posx > w - Math.round(clipWidth /2)) {
	xoverflow = posx - (w - Math.round(clipWidth/2));
      } 

      if (posy < clipHeight/2){
	yoverflow = posy - clipHeight/2;
      } else if (posy > h - Math.round(clipHeight/2)) {
	yoverflow = posy - (h - Math.round(clipHeight/2));
      } 
	
      overlay.style.top  = '-' + posy + "px";
      overlay.style.left = '-' + posx + "px";
      
      var clipTop   = (posy - findPosY(overlay)) - yoverflow - Math.round(clipHeight/2);
      var clipLeft  = (posx - findPosX(overlay)) - xoverflow - Math.round(clipWidth /2);
      var clipBot   = (clipTop + clipHeight);
      var clipRight = (clipLeft + clipWidth);
      var defClip = "rect(" + clipTop +"px "+ clipRight +"px "+ clipBot +"px "+ clipLeft +"px)";
      
      overlay.style.visibility = "visible";
      overlay.style.display = "block"; 
      overlay.style.clip = defClip;
    } else {
      alert('OOPS! looks like your browser sucks after all.');
    }
  } 
}

function showMap(event){
  showingMap = true;
  displayMap(event.pageX, event.pageY, event.clientX, event.clientY, 400, 400)
}

function hideMap(event){
  showingMap = false;
  var overlay = document.getElementById('overDiv');
  overlay.style.visibility = "hidden";
}

function toggleMap(event){
  if (showingMap){
    hideMap(event);
  } else {
    showMap(event);
  }
}

