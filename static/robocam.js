$(function(){
    var robocam = new (Backbone.View.extend({
        tagName: 'body',
        actions: {},
        events: {
            'keypress': 'handleKey'
        },

        registerAction: function(keyCode, callback) {
            this.actions[keyCode] = callback;
        },

        handleKey: function(e){
            var keyCode = e.keyCode;
            if (this.actions[keyCode]) {
                e.stopPropagation();
                this.actions[keyCode].call(null);
            }
        }
    }))({
        el: $('body')
    });

    new (Backbone.View.extend({
        tagName: 'div',
        hash: 0,
        imgU8: new jsfeat.matrix_t(800, 600, jsfeat.U8_t | jsfeat.C1_t),
        displayCorners: false,
        displayCanny: false,
        events: {
            'click #js-show-corners': 'handleShowCorners',
            'click #js-show-canny': 'handleShowCanny'
        },

        initialize: function(){
            this.corners = [];
            var i = 800*600;
            while(--i >= 0) {
                this.corners[i] = new jsfeat.point2d_t(0,0,0,0);
            }

            this.loadImage();
        },

        renderCorners: function(corners, count, img, step) {
            var pix = (0xff << 24) | (0x00 << 16) | (0xff << 8) | 0x00;
            for(var i=0; i < count; ++i)
            {
                var x = corners[i].x;
                var y = corners[i].y;
                var off = (x + y * step);
                img[off] = pix;
                img[off-1] = pix;
                img[off+1] = pix;
                img[off-step] = pix;
                img[off+step] = pix;
            }
        },

        showCorners: function(context){
            context.fillStyle = "rgb(0,255,0)";
            context.strokeStyle = "rgb(0,255,0)";

            var imageData = context.getImageData(0, 0, 800, 600);

            jsfeat.imgproc.grayscale(imageData.data, this.imgU8.data);

            jsfeat.fast_corners.set_threshold(20);

            var count = jsfeat.fast_corners.detect(this.imgU8, this.corners, 20);

            var data_u32 = new Uint32Array(imageData.data.buffer);
            this.renderCorners(this.corners, count, data_u32, 800);

            context.putImageData(imageData, 0, 0);
        },

        showCanny: function(context){
            var imageData = context.getImageData(0, 0, 800, 600);
            jsfeat.imgproc.grayscale(imageData.data, this.imgU8.data);

            var r = 2;
            var kernel_size = (r+1) << 1;

            jsfeat.imgproc.gaussian_blur(this.imgU8, this.imgU8, kernel_size, 0);
            
            jsfeat.imgproc.canny(this.imgU8, this.imgU8, 20, 50);

            var data_u32 = new Uint32Array(imageData.data.buffer);
            var alpha = (0xff << 24);
            var i = this.imgU8.cols*this.imgU8.rows, pix = 0;
            while(--i >= 0) {
                pix = this.imgU8.data[i];
                data_u32[i] = alpha | (pix << 16) | (pix << 8) | pix;
            }

            context.putImageData(imageData, 0, 0);
        },

        handleButton: function(e, attr) {
            this.displayCanny = false;
            this.displayCorners = false;

            var target = $(e.currentTarget);
            var active = target.hasClass('btn-success');
            this.$el.find('button').removeClass('btn-success');

            if (active) {
                this[attr] = false;
            } else {
                this[attr] = true;
                target.addClass('btn-success');
            }
        },

        handleShowCorners: function(e){
            this.handleButton(e, 'displayCorners');
        },

        handleShowCanny: function(e){
            this.handleButton(e, 'displayCanny');
        },

        loadImage: function(){
            var self = this;

            var canvas = this.$el.find('canvas')[0];
            var context = canvas.getContext('2d');
            var image = new Image();

            image.onload = function(){
                context.drawImage(image, 0, 0);
                self.hash++;

                if (self.displayCorners)
                    self.showCorners(context);

                if (self.displayCanny)
                    self.showCanny(context);

                self.loadImage();
            };
            image.src = '/camera/?i=' + this.hash;
        }
    }))({
        el: $('#js-camera-preview')
    });

    new (Backbone.View.extend({
        tagName: 'div',
        template: _.template($('#js-distance-tmpl').html()),
        distance: '',

        initialize: function(){
            this.receiveDistance();
        },

        receiveDistance: function(){
            var self = this;
            $.get('/distance/', function(data){
                self.distance = data;
                self.render();
                setTimeout($.proxy(self.receiveDistance, self), 300);
            })
        },

        render: function(){
            this.$el.html(this.template(this));
        }
    }))({
        el: $('#js-distance')
    });

    var ArmView = Backbone.View.extend({
        tagName: 'div',
        template: _.template($('#js-controller-tmpl').html()),
        events: {
            'click button': 'handleClick'
        },

        initialize: function() {
            this.initOptions();

            robocam.registerAction(
                this.options.leftKeyCode,
                $.proxy(function(){
                    this.handleAction(this.options.leftAction);
                }, this)
            );
            robocam.registerAction(
                this.options.rightKeyCode,
                $.proxy(function(){
                    this.handleAction(this.options.rightAction);
                }, this)
            );
        },

        initOptions: function(){
            this.options.leftKeyCode =
                this.options.leftKey.charCodeAt(0);
            this.options.rightKeyCode =
                this.options.rightKey.charCodeAt(0);
        },

        render: function(){
            this.$el.html(this.template(this.options));
        },

        handleAction: function(action){
            $.post('/arm/', {
                action: action,
                part: this.options.part
            });
        },

        handleClick: function(e){
            if ($(e.currentTarget).hasClass('js-left-btn'))
                this.handleAction(this.options.leftAction);
            else
                this.handleAction(this.options.rightAction);
        }
    });

    var actions = [
        ['grips', 'open', 'a', 'close', 'z'],
        ['wrist', 'up', 's', 'down', 'x'],
        ['elbow', 'up', 'd', 'down', 'c'],
        ['shoulder', 'up', 'f', 'down', 'v'],
        ['base', 'rotate_clock', 'g', 'rotate_counter', 'b'],
        ['led', 'on', 'q', 'off', 'w']
    ];

    var attrs = [
        'part',
        'leftAction', 'leftKey',
        'rightAction', 'rightKey'
    ];

    _.each(actions, function(params) {
        var options = _.object(_.map(attrs, function(attr, i){
            return [attr, params[i]];
        }));

        var view = new ArmView(options);
        view.render();
        $('#js-controller').append(view.$el);
    })
});
