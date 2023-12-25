L.Control.SliderControl = L.Control.extend({
    options: {
        position: 'topright',
        minValue: 0,
        maxValue: 100
    },

    initialize: function (options) {
        L.Util.setOptions(this, options);
    },

    onAdd: function (map) {
        let self = this;

        function valueChanged() {
            let lowStyle = ((self.lowValue - self.options.minValue) / (self.options.maxValue - self.options.minValue) * 100) + "%";
            let highStyle = ((self.highValue - self.options.minValue) / (self.options.maxValue - self.options.minValue) * 100) + "%";

            sliderB.style.setProperty("--low", lowStyle);
            sliderB.style.setProperty("--high", highStyle);

            $(self).trigger("update");
        }

        function createSlider(className, value) {
            let slider = L.DomUtil.create('input', className, controlHost);

            function updateAttributes() {
                $(slider).attr('value', slider.value);

                let ratio = (slider.value - self.options.minValue) / (self.options.maxValue - self.options.minValue);

                let sliderWidth = $(slider).width();
                let thumbWidth = 20; // need better magic to get rid of this

                let pos = ratio * (sliderWidth - thumbWidth) + 6;

                slider.style.setProperty("--thumb-label-pos", pos + "px");
            }

            $(slider)
                .attr("type", "range")
                .attr("min", self.options.minValue)
                .attr("max", self.options.maxValue)
                .attr("value", value)
                .mousedown(() => map.dragging.disable())
                .mouseup(() => map.dragging.enable())
                .on("input", function () {
                    updateAttributes();
                    valueChanged();
                });

            updateAttributes();

            return slider;
        }

        let controlHost = L.DomUtil.create('div', 'leaflet-slider', this._container);
        if (this.options.className) {
            $(controlHost).addClass(this.options.className);
        }
        if (this.options.label) {
            let label = L.DomUtil.create('div', "leaflet-slider-label", controlHost);
            $(label).text(this.options.label);
        }

        $(controlHost)
            .mouseover(() => {
                map.disableMouse = true;
                map.fire("mouseout");
            })
            .mouseout(() => {
                map.disableMouse = false;
            });


        let sliderA = createSlider("alpha", this.options.lowValue || this.options.minValue);
        let sliderB = createSlider("beta", this.options.highValue || this.options.maxValue);

        Object.defineProperties(this, {
            lowValue: {
                get: function () {
                    return Math.min(sliderA.value, sliderB.value);
                },
                set: function (v) {
                    if (sliderA.value <= sliderB.value)
                        sliderA.value = v;
                    else
                        sliderB.value = v;
                },
                enumerable: true
            },
            highValue: {
                get: function () {
                    return Math.max(sliderA.value, sliderB.value);
                },
                set: function (v) {
                    if (sliderA.value > sliderB.value)
                        sliderA.value = v;
                    else
                        sliderB.value = v;
                },
                enumerable: true
            }
        });

        setTimeout(() => {
            // delay resetting the slider positions until leaflet finishes adding the control
            $(sliderA).trigger("input");
            $(sliderB).trigger("input");
        });

        return controlHost;
    },

    onRemove: function (map) {

    }
});
