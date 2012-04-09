import "utils.js";
import "core.js";
import "anim.js";
import "handlers.js";

var avatar1, avatar2, background, lbl1, lbl2;

function splash_init() {
   background = new Anim({ 'img':medias[2], 'scale':500, 'opacity':0.2, 'x':-60, 'y':-50, 'width':75, 'height':75 });

   avatar1 = new Anim({ 'scale':0, 'opacity':0, 'img':medias[0], 'x':80, 'y':65, 'width':100, 'height':100 });
   avatar1.animate({ 'scale':100, 'opacity':1, 'duration':0.5 }, function() {
      lbl1 = new Label({ 'text':'@Masque', 'x': -170, 'y':140, 'font':'25px sans-serif' });
      lbl1.animate({'to':new Point(13, 140), 'duration':1, 'effect':'>'}, function() {
      
         avatar2 = new Anim({ 'scale':0, 'opacity':0, 'img':medias[1], 'x':230, 'y':65, 'width':130, 'height':90 });
         avatar2.animate({ 'scale':100, 'opacity':1, 'duration':0.5 }, function() {
            
            lbl2 = new Label({ 'text':'DJ Wooooo', 'x': 300, 'y':140, 'font':'25px sans-serif' });
            lbl2.animate({'to':new Point(160, 140), 'duration':1, 'effect':'bounce'});
         });
      });
   });


}


fw.main('canvas', 30, 300, 150, 1,
   fw.Loader.extend({
      files:["avatar1.png", "avatar2.png", "record.png"],
      end: function() {
         switchState('splash');
      }
   })
);
