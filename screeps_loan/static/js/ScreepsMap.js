
var ScreepsMap = function() {
    // Magic values
    this.containerID = "ScreepsMapContainer";
    this.canvasID = "ScreepsMapCanvas";
    this.colorKeyID = "ScreepsColorKeyContainer";
    this.topLeftOfTerrain = this.roomNameToXY("W60N60");
    this.terrainImageRoomSize = 50;

    // Defaults
    this.setRoomSize(5,5);
    this.setMapBounds("W70N70","E70S70");
    this.setPadding(5);
};

ScreepsMap.prototype.colors = ["#FF0", "#6A6","#66F","#F6A","#6AA","#06A","#0A6","#6A0","#A06","#60A"];

ScreepsMap.prototype.setRoomSize = function(width, height) {
    this.roomWidth = width;
    if (!height) {
        height = width;
    }
    this.roomHeight = height;
}

ScreepsMap.prototype.setPadding = function(padding) {
    this.padding = padding;
}

ScreepsMap.prototype.setMapBounds = function(topLeft, bottomRight) {
    this.topLeft = this.roomNameToXY(topLeft);
    this.bottomRight = this.roomNameToXY(bottomRight);
}

ScreepsMap.prototype.setRoomData = function(data) {
    this.rooms = data;
}

ScreepsMap.prototype.setAllianceData = function(data) {
    this.alliances = data;
    this.allianceNames = Object.keys(this.alliances);
    this.allianceNames.sort();

    this.alliances['neutral'] = {
      'name': 'unaffiliated',
      'members': ['neutral'],
      'color': '#474747'
    }
    this.allianceNames.push('neutral')
}

ScreepsMap.prototype.desiredCanvasWidth = function() {
    return (this.bottomRight.x + 1 - this.topLeft.x) * this.roomWidth + 2 * this.padding;
}

ScreepsMap.prototype.desiredCanvasHeight = function() {
    return (this.bottomRight.y + 1 - this.topLeft.y) * this.roomHeight + 2 * this.padding;
}

ScreepsMap.prototype.roomNameToXY = function(name) {
    let parts = name.match(/([EW])([0-9]*)([NS])([0-9]*)/);
    let x = parseInt(parts[2]);
    if (parts[1] == "W") {
        x = ~x;
    }
    let y = parseInt(parts[4]);
    if (parts[3] == "N") {
        y = ~y;
    }
    return {"x": x, "y": y};
}

ScreepsMap.prototype.xyToRoomName = function(xy) {
    let result = "";
    result += (xy.x < 0 ? "W" + String(~xy.x) : "E" + String(xy.x));
    result += (xy.y < 0 ? "N" + String(~xy.y) : "S" + String(xy.y));
    return result;
}

ScreepsMap.prototype.roomNameToRoomCorner = function(name) {
    let xy = this.roomNameToXY(name);
    xy.x = this.padding + (xy.x - this.topLeft.x)*this.roomWidth;
    xy.y = this.padding + (xy.y - this.topLeft.y)*this.roomHeight;
    return xy;
}

ScreepsMap.prototype.roomNameToRoomCenter = function(name) {
    let xy = this.roomNameToRoomCorner(name);
    xy.x += 0.5*this.roomWidth;
    xy.y += 0.5*this.roomHeight;
    return xy;
}

ScreepsMap.prototype.hexToRgb = function(hex) {
    let shorthandRegex = /^#?([a-fA-F0-9])([a-fA-F0-9])([a-fA-F0-9])$/;
    hex = hex.replace(shorthandRegex, function(m, r, g, b) {
        return r + r + g + g + b + b;
    });
    let result = /^#?([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})$/.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

ScreepsMap.prototype.colorForAlliance = function(aName) {
    if(!this.alliances[aName].color) {
      if(this.colors.length > 0) {
        this.alliances[aName].color = this.colors.shift()
      } else {
        var colorInt = Math.floor(Math.random() * (4096 - 0 + 1)) + 0;
        this.alliances[aName].color = '#' + colorInt.toString(16)
      }
    }
    return this.alliances[aName].color
}

ScreepsMap.prototype.drawAllianceMap = function(options) {
    this.canvas = this.resetCanvas(document.getElementById(this.containerID));
    this.context = this.canvas.getContext("2d");
    this.drawOptions = options;
    if (!this.drawOptions.roomStyle) {
        this.drawOptions.roomStyle = "box";
    }
    this.loadImages(function() {
        this.drawTerrain();
        this.drawAlliances();
    }.bind(this));
}

ScreepsMap.prototype.resetCanvas = function(container) {
    let canvasHTML = '<canvas id="' + this.canvasID + '" width="' + this.desiredCanvasWidth() + '" height="' + this.desiredCanvasHeight() + '"></canvas>';
    container.innerHTML = canvasHTML;
    return document.getElementById(this.canvasID);
}

ScreepsMap.prototype.loadImages = function(callback) {
    this.terrainImage = new Image();
    this.terrainImage.src = "/static/img/screeps_terrain.png";
    this.terrainImage.onload = callback;
}

ScreepsMap.prototype.drawTerrain = function() {
    let clipX = (this.topLeft.x - this.topLeftOfTerrain.x) * this.terrainImageRoomSize;
    let clipY = (this.topLeft.y - this.topLeftOfTerrain.y) * this.terrainImageRoomSize;
    let clipWidth = (this.bottomRight.x - this.topLeft.x + 1) * this.terrainImageRoomSize;
    let clipHeight = (this.bottomRight.y - this.topLeft.y + 1) * this.terrainImageRoomSize;
    let imageWidth = (this.bottomRight.x - this.topLeft.x + 1) * this.roomWidth;
    let imageHeight = (this.bottomRight.y - this.topLeft.y + 1) * this.roomHeight;
    this.context.save();
    this.context.globalAlpha = 0.7;
    this.context.drawImage(this.terrainImage, clipX, clipY, clipWidth, clipHeight, this.padding, this.padding, imageWidth, imageHeight);
    this.context.restore();
}

ScreepsMap.prototype.drawAlliances = function() {
    for (let name of Object.keys(this.rooms)) {
        for (let aName of Object.keys(this.alliances)) {
            if (this.alliances[aName].members.indexOf(this.rooms[name].owner) != -1) {
                if (this.drawOptions.roomStyle == "blob") {
                    if (this.rooms[name].level) {
                        this.drawFadeCircle(name, this.roomWidth*2, this.roomWidth*0.7, this.colorForAlliance(aName));
                    } else {
                        this.drawFadeCircle(name, this.roomWidth*0.7, this.roomWidth*0.1, this.colorForAlliance(aName));
                    }
                } else {
                    this.drawFillBox(name, this.colorForAlliance(aName), (this.rooms[name].level > 0 ? 1 : 0.5));
                }
            }
        }
    }
}

ScreepsMap.prototype.drawFadeCircle = function(roomName, radius, solidRadius, color) {
    let xy = this.roomNameToRoomCenter(roomName);
    this.context.beginPath();
    let rad = this.context.createRadialGradient(xy.x, xy.y, solidRadius, xy.x, xy.y, radius);
    let parts = this.hexToRgb(color);
    rad.addColorStop(0, 'rgba(' + parts.r + ', ' + parts.g + ', ' + parts.b + ',1)');
    rad.addColorStop(1, 'rgba(' + parts.r + ', ' + parts.g + ', ' + parts.b + ',0)');
    this.context.fillStyle = rad;
    this.context.arc(xy.x, xy.y, radius, 0, Math.PI*2, false);
    this.context.fill();
}

ScreepsMap.prototype.drawFillBox = function(roomName, color, alpha) {
    let xy = this.roomNameToRoomCorner(roomName);
    this.context.save();
    this.context.fillStyle = color;
    this.context.globalAlpha = alpha;
    this.context.fillRect(xy.x, xy.y, this.roomWidth, this.roomHeight);
    this.context.restore();
}

ScreepsMap.prototype.drawColorKey = function() {
    let container = document.getElementById(this.colorKeyID);
    let output = '<ul class="colorKeyList">';
    for (let aName of this.allianceNames) {
        output += '<li class="colorKeyItem"><span class="colorBox" style="background-color: ' + this.colorForAlliance(aName) + ';"></span>';
        output += '<span class="colorLabel">' + this.alliances[aName].name + '</li>';
    }
    output += '</ul>';
    container.innerHTML = output;
}

