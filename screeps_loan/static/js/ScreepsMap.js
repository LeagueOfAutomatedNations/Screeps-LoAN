var DEFAULT_COLORS = [
    '#FF0',
    '#E0FFFF',
    '#ADFF2F',
    '#F0E68C',
    '#FF00FF',
    '#FFE4E1',
    '#F6A',
    '#FF4500',
    '#00FF00',
    '#DDA0DD',
    '#D00000',
    '#60A'
];

var DEFAULT_UNCATEGORIZED = '#555'

var ScreepsMap = (function() {
    function ScreepsMap (config) {
        this.spinnerHostId = config.spinnerHostId;
        this.mapHostId = config.mapHostId;
        this.legendHostId = config.legendHostId;
        this.roomTooltipHostId = config.roomTooltipHostId;

        this.terrainUri = config.terrainUri;
        this.region = config.region;

        this.legendUrlPrefix = config.legendUrlPrefix
        this.groupType = 'alliance'
        this.userColors = {}
        this.style = config.style || {};
    }

    ScreepsMap.prototype.setData = function (roomData, allianceData) {
        this.roomData = roomData;
        this.allianceData = allianceData;

        this.allianceData['unaffiliated'] = {
            'name': 'unaffiliated',
            'members': ["neutral"],
            'color': DEFAULT_UNCATEGORIZED
        };

        // build user -> alliance lookup
        this.userAlliance = {};
        for (let allianceName in this.allianceData) {
            let alliance = this.allianceData[allianceName];
            for (let userIndex in alliance.members) {
                let userName = alliance.members[userIndex];
                this.userAlliance[userName] = allianceName;
            }
        }
    }

    ScreepsMap.prototype.setAlliance = function (alliance) {
      this.alliance = alliance
    }

    ScreepsMap.prototype.allowUnaffiliated = function () {
      this.allowUnaffiliated = true
    }

    ScreepsMap.prototype.disableLabels = function () {
      this.disableLabels = true
    }

    ScreepsMap.prototype.setGroupType = function (type) {
      this.groupType = type
      if(type == 'user') {
        this.legendUrlPrefix = 'https://screeps.com/a/#!/profile/'
      }
    }

    ScreepsMap.prototype.setSpinnerVisibile = function (show) {
        let container = document.getElementById(this.spinnerHostId);
        container.className = (show)
            ? "spinner"
            : "";
    }

    ScreepsMap.prototype.render = function () {
        this.setSpinnerVisibile(true);

        this.loadTerrainAsync(function() {
            let regionBounds = this.getRegionBounds();

            let mapAdjust = (this.style['room-padding'] || 0) * ScreepsConstants.RoomSize;
            let mapBounds = [
                [
                    regionBounds[0][0] + mapAdjust,
                    regionBounds[0][1] - mapAdjust,
                ],
                [
                    regionBounds[1][0] - mapAdjust,
                    regionBounds[1][1] + mapAdjust,
                ]
            ];

            this.map = L.map(this.mapHostId, {
                crs: L.CRS.Simple,
                minZoom: -3.5,
                maxZoom: 1,
                zoomSnap: 0.1,
                zoomDelta: 0.75,
                attributionControl: false
            });
            this.map.fitBounds(mapBounds);

            let controlLayer = (new L.LayerGroup()).addTo(this.map);
            let labelLayer = (new L.LayerGroup()).addTo(this.map);
            let terrainLayer = L.tileLayer(
                "/static/img/map/{z}/tile_{x}_{y}.png",
                {
                    minZoom: -4,
                    maxNativeZoom: 0,
                    tileSize: 200,
                    bounds: regionBounds,
                    noWrap: true,
                    tms: false
                }
            ).addTo(this.map);

            this.drawRoomLayer(controlLayer);
            this.drawLabelLayer(labelLayer);

            let overlays = {
                "Terrain": terrainLayer,
                "Rooms": controlLayer,
                "Labels": labelLayer
            };
            L.control.layers({}, overlays).addTo(this.map);

            if (this.groupType == 'user') {
                this.drawUserLegend();
            } else {
                this.drawAllianceLegend();
            }

            this.createRoomInfoControl();

            this.setSpinnerVisibile(false);
        }.bind(this));
    }

    ScreepsMap.prototype.createRoomInfoControl = function () {
        let roomInfoControl = document.getElementById(this.roomTooltipHostId);
        let self = this;
        roomInfoControl.update = function (e, roomName) {
            if (roomName) {
                let toolRect = this.getBoundingClientRect();
                this.style.left = String(e.originalEvent.clientX + 15) + "px";
                this.style.top = String(e.originalEvent.clientY - Math.floor(toolRect.height/2)) + "px";
                this.style.display = "block";

                if (this.currentRoom === roomName) return;
                self.populateTooltip(this, roomName);

            } else {
                this.style.display = "none";
            }

            this.currentRoom = roomName;
        };

        this.map.on({
            click: function(e) {
                let worldPosition = this.worldPositionFromMapCoords(e.latlng);

                if (this.region.worldPositionInBounds(worldPosition.x, worldPosition.y)) {
                    let roomName = this.region.worldPositionToRoomName(worldPosition.x, worldPosition.y);
                    window.open("https://screeps.com/a/#!/room/" + roomName, "loan-launch-tab");
                }
            }.bind(this),

            mouseover: function(e) {
                let worldPosition = this.worldPositionFromMapCoords(e.latlng);

                let roomName;
                if (this.region.worldPositionInBounds(worldPosition.x, worldPosition.y)) {
                    roomName = this.region.worldPositionToRoomName(worldPosition.x, worldPosition.y);
                }

                roomInfoControl.update(e, roomName);
            }.bind(this),

            mousemove: function(e) {
                let worldPosition = this.worldPositionFromMapCoords(e.latlng);

                let roomName;
                if (this.region.worldPositionInBounds(worldPosition.x, worldPosition.y)) {
                    roomName = this.region.worldPositionToRoomName(worldPosition.x, worldPosition.y);
                }

                roomInfoControl.update(e, roomName);
            }.bind(this),

            mouseout: function(e) {
                roomInfoControl.update(e, null);
            }.bind(this),
        });
    }

    ScreepsMap.prototype.populateTooltip = function (tooltip, roomName) {
        tooltip.querySelector(".roomName").innerHTML = roomName;
        if (this.roomData[roomName]) {
            if (this.roomData[roomName].level) {
                tooltip.querySelector(".roomType").innerHTML = "Owned";
                tooltip.querySelector(".roomLevel").innerHTML = this.roomData[roomName].level;
            } else {
                tooltip.querySelector(".roomType").innerHTML = "Reserved";
                tooltip.querySelector(".roomLevel").innerHTML = "N/A";
            }
            tooltip.querySelector(".roomOwner").innerHTML = this.roomData[roomName].owner;

            let allianceName = this.userAlliance[this.roomData[roomName].owner];
            if (allianceName && this.allianceData[allianceName]) {
                tooltip.querySelector(".roomAlliance").innerHTML = this.allianceData[allianceName].name;
            } else {
                tooltip.querySelector(".roomAlliance").innerHTML = "unaffiliated";
            }
        } else {
            tooltip.querySelector(".roomType").innerHTML = "Unowned";
            tooltip.querySelector(".roomOwner").innerHTML = "N/A";
            tooltip.querySelector(".roomAlliance").innerHTML = "N/A";
            tooltip.querySelector(".roomLevel").innerHTML = "N/A";
        }
    }

    ScreepsMap.prototype.drawAllianceLegend = function () {
        let container = document.getElementById(this.legendHostId);
        let output = '<h3>Legend:</h3>';
        output += '<ul class="colorKeyList">';
        for (let allianceName in this.allianceData) {
            output += '<div id=#colorkey_alliance_' + allianceName + '>'
            output += '  <li class="colorKeyItem">';
            output += '    <span class="colorBox" style="background-color: ' + this.getAllianceColor(allianceName) + ';"></span>';
            output += '    <a href="' + this.legendUrlPrefix + this.allianceData[allianceName].abbreviation + '">'
            output += '      <span class="colorLabel">' + this.allianceData[allianceName].name + '</span>';
            output += '    </a>';
            output += '  </li>';
            output += '</div>';
        }
        output += '</ul>';
        container.innerHTML = output;
    }

    ScreepsMap.prototype.drawUserLegend = function () {
        let container = document.getElementById(this.legendHostId);
        let output = '<h3>Legend:</h3>';
        output += '<ul class="colorKeyList">';
        for (let user in this.userAlliance) {
            if(!!this.alliance && this.alliance != this.userAlliance[user]) {
              continue
            }
            output += '<div id=#colorkey_alliance_' + user + '>'
            output += '  <li class="colorKeyItem">';
            output += '    <span class="colorBox" style="background-color: ' + this.getUserColor(user) + ';"></span>';
            output += '    <a href="' + this.legendUrlPrefix + user + '">'
            output += '      <span class="colorLabel">' + user + '</span>';
            output += '    </a>';
            output += '  </li>';
            output += '</div>';
        }
        output += '</ul>';
        container.innerHTML = output;
    }


    ScreepsMap.prototype.loadTerrainAsync = function (callback) {
        this.terrainImage = new Image();
        this.terrainImage.src = this.terrainUri;
        this.terrainImage.onload = callback;
    }

    ScreepsMap.prototype.drawRoomLayer = function (controlLayer) {
        let allianceLayers = {};
        for (let allianceName in this.allianceData) {
            allianceLayers[allianceName] = new L.LayerGroup();
            controlLayer.addLayer(allianceLayers[allianceName]);
        }

        for (let roomName in this.roomData) {
            let room = this.roomData[roomName];
            let rect = this.region.getRoomRect(roomName);
            let bounds = this.rectToBounds(rect);

            if (room.owner) {
                let allianceName = this.userAlliance[room.owner];
                if(!allianceName) {
                  allianceName = 'unaffiliated'
                }
                let targetLayer = allianceLayers[allianceName];
                let fillColor = this.getUserColor(room.owner);
                let fillOpacity = (room.level !== 0) ? 0.75 : 0.5;

                L.rectangle(bounds, { stroke: false, fillColor: fillColor, fillOpacity: fillOpacity, interactive: false }).addTo(targetLayer);
            }
        }
    }

    ScreepsMap.prototype.drawLabelLayer = function (labelLayer) {
        let groups = this.findGroups(10);
        for (let group of groups) {
            let allianceName = this.groupType == 'user' ? this.userAlliance[group.labelName] : group.labelName
            let alliance = this.allianceData[allianceName];
            if(!alliance || alliance.name == 'unaffiliated') {
              if(!this.allowUnaffiliated) {
                continue
              }
            }
            if(!!this.alliance) {
              if(!alliance) {
                continue
              }
              if(this.alliance !== alliance.abbreviation) {
                continue
              }
            }
            let center = this.geometricCenter(group.rooms);
            if(this.groupType == 'user') {
              var title = group.labelName
              var color = this.getUserColor(group.labelName)
            } else {
              if(!alliance) {
                continue
              }
              var title = !!alliance.abbreviation ? alliance.abbreviation : alliance.name;
              var color = this.getAllianceColor(group.labelName)
            }
            L.marker([~center.y, center.x], {
                icon: L.divIcon({
                    className: 'alliance-label',
                    html: "<span style='color:" + color + "'>" + title + "</span>",
                    interactive: false
                })
            }).addTo(labelLayer);
        }
    }

    ScreepsMap.prototype.geometricCenter = function (rooms) {
        // average top left coordinates
        let sum = {x: 0, y: 0};
        for (let name of rooms) {
            let rect = this.region.getRoomRect(name);
            sum.x += rect.left;
            sum.y += rect.top;
        }
        sum.x = Math.floor(sum.x / rooms.length);
        sum.y = Math.floor(sum.y / rooms.length);

        // adjust for center
        sum.x = Math.floor((sum.x + .5 * ScreepsConstants.RoomSize));
        sum.y = Math.floor((sum.y + .5 * ScreepsConstants.RoomSize));

        return sum;
    }

    ScreepsMap.prototype.findGroups = function (radius) {
        let results = [];
        let checked = {};

        let topLeft = this.region.roomNameToXY(this.region.topLeft);
        let bottomRight = this.region.roomNameToXY(this.region.bottomRight);

        // iterate over each room
        for (let y = topLeft.y; y <= bottomRight.y; y++) {
            for (let x = topLeft.x; x <= bottomRight.x; x++) {
                let roomName = this.region.xyToRoomName(x, y);

                // ignore rooms that were already scanned by the loop below
                if (checked[roomName]) continue;
                checked[roomName] = true;

                // ignore unclaimed rooms
                let room = this.roomData[roomName];
                if (!room || !room.owner) continue;

                // ignore rooms owned by unaffiliated players
                let allianceName = this.userAlliance[room.owner];
                if (allianceName === "unaffiliated" && !this.allowUnaffiliated) continue;

                if(this.groupType == 'user') {
                  var labelName = room.owner
                } else {
                  var labelName = allianceName
                }


                // start building a new group
                let rooms = [roomName];

                // Check every room in a (2*radius+1)x(2*radius+1) square around the current room. If
                // we find a room owned by the current alliance, push it onto the stack to be searched next.
                let groupChecked = {};
                let toCheck = [roomName];
                while (toCheck.length > 0) {
                    let checkName = toCheck.pop();
                    let xy = this.region.roomNameToXY(checkName);

                    let minXY = {"x": Math.max(topLeft.x, xy.x - radius), "y": Math.max(topLeft.y, xy.y - radius)};
                    let maxXY = {"x": Math.min(bottomRight.x, xy.x + radius), "y": Math.min(bottomRight.y, xy.y + radius)};
                    for (let y = minXY.y; y <= maxXY.y; y++) {
                        for (let x = minXY.x; x <= maxXY.x; x++) {
                            if (y === minXY.y && x <= xy.x) continue;

                            let curName = this.region.xyToRoomName(x, y);
                            let curRoom = this.roomData[curName];
                            if (!curRoom || !curRoom.owner) continue;

                            if (groupChecked[curName] || checked[curName]) continue;
                            groupChecked[curName] = true;

                            var curLabel = this.groupType == 'user' ? curRoom.owner : this.userAlliance[curRoom.owner];
                            if(this.groupType != 'user') {
                              let curAlliance = this.userAlliance[curRoom.owner];
                              if (curAlliance === "unaffiliated" && !this.allowUnaffiliated) continue;
                            }
                            if (curLabel === labelName) {
                                checked[curName] = true;
                                toCheck.push(curName);
                                rooms.push(curName);
                            }
                        }
                    }
                }

                // save the completed group
                results.push({
                    labelName,
                    rooms
                });
            }
        }

        return results;
    }

    ScreepsMap.prototype.getRegionBounds = function () {
        let regionRect = this.region.getRect();
        return this.rectToBounds(regionRect);
    }

    ScreepsMap.prototype.rectToBounds = function (rect) {
        return [[~rect.top, rect.left], [~rect.bottom, rect.right]];
    }

    ScreepsMap.prototype.worldPositionFromMapCoords = function (latlng) {
        return {
            x: latlng.lng,
            y: ~latlng.lat
        };
    }

    ScreepsMap.prototype.getUserColor = function (user) {
      let allianceName = this.userAlliance[user];
      if(!this.allowUnaffiliated) {
        if(!allianceName) {
          return DEFAULT_UNCATEGORIZED
        }
      }
      if(!!this.alliance && this.alliance != allianceName) {
        return DEFAULT_UNCATEGORIZED
      }

      if(this.groupType == 'user') {
        if(!this.userColors[user]) {
          this.userColors[user] = this.getRandomColor(user)
        }
        return this.userColors[user]
      }
      return this.getAllianceColor(allianceName)
    }

    ScreepsMap.prototype.getAllianceColor = function (allianceName) {
      if (!allianceName || !this.allianceData[allianceName]) {
       allianceName = 'unaffiliated'
      }

      if (!this.allianceData[allianceName].color) {
          if (DEFAULT_COLORS.length > 0) {
              this.allianceData[allianceName].color = DEFAULT_COLORS.shift()
          } else {
              this.allianceData[allianceName].color = this.getRandomColor(allianceName)
          }
      }
      return this.allianceData[allianceName].color
    }

    ScreepsMap.prototype.getRandomColor = function (seed=false) {
      if (DEFAULT_COLORS.length > 0) {
          return DEFAULT_COLORS.shift()
      }

      if(!!seed) {
        seed = parseInt(seed.replace(/[^0-9a-z]/gi, ''), 36) % 10000000
      } else {
        if(!this.seed) {
          this.seed = 1000
        } else {
          this.seed += 1
        }
        seed = this.seed
      }

      let luminosity = seed % 4 == 0 ? 'bright' : 'light'
      return randomColor({
        luminosity: luminosity,
        hue: 'random',
        seed: seed
      });
    }

    return ScreepsMap;
})();

/*
 * Workaround for 1px lines appearing in some browsers due to fractional transforms
 * and resulting anti-aliasing.
 * https://github.com/Leaflet/Leaflet/issues/3575
 */
(function(){
    var originalInitTile = L.GridLayer.prototype._initTile
    L.GridLayer.include({
        _initTile: function (tile) {
            originalInitTile.call(this, tile);

            var tileSize = this.getTileSize();

            tile.style.width = tileSize.x + 1 + 'px';
            tile.style.height = tileSize.y + 1 + 'px';
        }
    });
})()