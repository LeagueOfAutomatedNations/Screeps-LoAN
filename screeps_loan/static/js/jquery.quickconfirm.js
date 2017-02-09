(function($) {
   $.fn.quickConfirm = function() {
       this.click(function(event) {
           event.preventDefault();
           $.ajax(this.href, {
               dataType: 'json',
               method: 'POST',
               success: function(data) {
                  console.log('success')
                   modal = $(this.self).data('confirmationModal')
                   if (!modal) {
                       modal = '#confirmationModal'
                   }
                   console.log(modal)
                   var popup = new Foundation.Reveal($(modal));
                   popup.open();
               }.bind({
                   self: this
               }),
               error: function() {
                   console.log('error')
                   var popup = new Foundation.Reveal($('#errorModal'));
                   popup.open();
               }
           });
           return this;
       });
   }
}(jQuery));
