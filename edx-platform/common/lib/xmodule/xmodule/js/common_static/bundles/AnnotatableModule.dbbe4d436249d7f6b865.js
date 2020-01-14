!function(t,e){for(var o in e)t[o]=e[o]}(window,webpackJsonp([21],{"./common/static/xmodule/modules/js/002-e32c61651b0379c8503ad932a91e7651.js":function(t,o,n){(function(t){(function(){(function(){var o=function(t,e){return function(){return t.apply(e,arguments)}};this.Annotatable=function(){function n(e){this.onMoveTip=o(this.onMoveTip,this),this.onShowTip=o(this.onShowTip,this),this.onClickReturn=o(this.onClickReturn,this),this.onClickReply=o(this.onClickReply,this),this.onClickToggleInstructions=o(this.onClickToggleInstructions,this),this.onClickToggleAnnotations=o(this.onClickToggleAnnotations,this),this._debug&&console.log("loaded Annotatable"),this.el=e,this.$el=t(e),this.init()}return n.prototype._debug=!1,n.prototype.wrapperSelector=".annotatable-wrapper",n.prototype.toggleAnnotationsSelector=".annotatable-toggle-annotations",n.prototype.toggleInstructionsSelector=".annotatable-toggle-instructions",n.prototype.instructionsSelector=".annotatable-instructions",n.prototype.sectionSelector=".annotatable-section",n.prototype.spanSelector=".annotatable-span",n.prototype.replySelector=".annotatable-reply",n.prototype.problemXModuleSelector=".xmodule_CapaModule",n.prototype.problemSelector="div.problem",n.prototype.problemInputSelector="div.problem .annotation-input",n.prototype.problemReturnSelector="div.problem .annotation-return",n.prototype.$=function(e){return t(e,this.el)},n.prototype.init=function(){return this.initEvents(),this.initTips()},n.prototype.initEvents=function(){var e;return e=[!1,!1],this.annotationsHidden=e[0],this.instructionsHidden=e[1],this.$(this.toggleAnnotationsSelector).bind("click",this.onClickToggleAnnotations),this.$(this.toggleInstructionsSelector).bind("click",this.onClickToggleInstructions),this.$el.on("click",this.replySelector,this.onClickReply),t(document).on("click",this.problemReturnSelector,this.onClickReturn)},n.prototype.initTips=function(){return this.$(this.spanSelector).each(function(e){return function(o,n){return t(n).qtip(e.getSpanTipOptions(n))}}(this))},n.prototype.getSpanTipOptions=function(e){return{content:{title:{text:this.makeTipTitle(e)},text:this.makeTipContent(e)},position:{my:"bottom center",at:"top center",target:t(e),container:this.$(this.wrapperSelector),adjust:{y:-5}},show:{event:"click mouseenter",solo:!0},hide:{event:"click mouseleave",delay:500,fixed:!0},style:{classes:"ui-tooltip-annotatable"},events:{show:this.onShowTip,move:this.onMoveTip}}},n.prototype.onClickToggleAnnotations=function(t){return this.toggleAnnotations()},n.prototype.onClickToggleInstructions=function(t){return this.toggleInstructions()},n.prototype.onClickReply=function(t){return this.replyTo(t.currentTarget)},n.prototype.onClickReturn=function(t){return this.returnFrom(t.currentTarget)},n.prototype.onShowTip=function(t,e){if(this.annotationsHidden)return t.preventDefault()},n.prototype.onMoveTip=function(e,o,n){var i,r,l,s,c,a,u,p,d,f,h,g,m,b,y,v,T,S,C,x;return y=o.elements.tooltip,i=(null!=(h=o.options.position)&&null!=(g=h.adjust)?g.y:void 0)||0,r=(null!=(m=o.options.position)?m.container:void 0)||t("body"),b=o.elements.target,f=t(b).get(0).getClientRects(),c=2===(null!=f?f.length:void 0)&&f[0].left>f[1].right,s=c?f[0].width>f[1].width?f[0]:f[1]:f[0],p=s.left+s.width/2,d=s.top,C=t(y).width(),v=t(y).height(),l=t(r).offset(),a=-l.left,u=t(document).scrollTop()-l.top,T=a+p-C/2,S=u+d-v+i,x=t(window).width(),T<a?T=a:T+C>x+a&&(T=x+a-C),t.extend(n,{left:T,top:S})},n.prototype.getSpanForProblemReturn=function(e){var o;return o=t(this.problemReturnSelector).index(e),this.$(this.spanSelector).filter("[data-problem-id='"+o+"']")},n.prototype.getProblem=function(e){var o;return o=this.getProblemId(e),t(this.problemInputSelector).eq(o)},n.prototype.getProblemId=function(e){return t(e).data("problem-id")},n.prototype.toggleAnnotations=function(){var t;return t=this.annotationsHidden=!this.annotationsHidden,this.toggleAnnotationButtonText(t),this.toggleSpans(t),this.toggleTips(t)},n.prototype.toggleTips=function(t){var e;return e=this.findVisibleTips(),this.hideTips(e)},n.prototype.toggleAnnotationButtonText=function(t){var e;return e=t?gettext("Show Annotations"):gettext("Hide Annotations"),this.$(this.toggleAnnotationsSelector).text(e)},n.prototype.toggleInstructions=function(){var t;return t=this.instructionsHidden=!this.instructionsHidden,this.toggleInstructionsButton(t),this.toggleInstructionsText(t)},n.prototype.toggleInstructionsButton=function(t){var e,o;return o=t?gettext("Expand Instructions"):gettext("Collapse Instructions"),e=t?["expanded","collapsed"]:["collapsed","expanded"],this.$(this.toggleInstructionsSelector).text(o).removeClass(e[0]).addClass(e[1])},n.prototype.toggleInstructionsText=function(t){var e;return e=t?"slideUp":"slideDown",this.$(this.instructionsSelector)[e]()},n.prototype.toggleSpans=function(t){return this.$(this.spanSelector).toggleClass("hide",t,250)},n.prototype.replyTo=function(t){var o,n;return n=-20,o=this.getProblem(t),o.length>0?this.scrollTo(o,this.afterScrollToProblem,n):this._debug?console.log("problem not found. event: ",e):void 0},n.prototype.returnFrom=function(t){var o,n;return n=-200,o=this.getSpanForProblemReturn(t),o.length>0?this.scrollTo(o,this.afterScrollToSpan,n):this._debug?console.log("span not found. event:",e):void 0},n.prototype.scrollTo=function(e,o,n){if(null==n&&(n=-20),t(e).length>0)return t("html,body").scrollTo(e,{duration:500,onAfter:this._once(function(t){return function(){return null!=o?o.call(t,e):void 0}}(this)),offset:n})},n.prototype.afterScrollToProblem=function(t){return t.effect("highlight",{},500)},n.prototype.afterScrollToSpan=function(t){return t.addClass("selected",400,"swing",function(){return t.removeClass("selected",400,"swing")})},n.prototype.makeTipContent=function(e){return function(o){return function(n){var i,r,l,s;return s=t(e).data("comment-body"),i=o.createComment(s),r=o.getProblemId(e),l=o.createReplyLink(r),t(i).add(l)}}(this)},n.prototype.makeTipTitle=function(e){return function(o){return function(o){return t(e).data("comment-title")||gettext("Commentary")}}()},n.prototype.createComment=function(e){return t('<div class="annotatable-comment">'+e+"</div>")},n.prototype.createReplyLink=function(e){var o;return o=gettext("Reply to Annotation"),t('<a class="annotatable-reply" href="javascript:void(0);" data-problem-id="'+e+'">'+o+"</a>")},n.prototype.findVisibleTips=function(){var e;return e=[],this.$(this.spanSelector).each(function(o,n){var i,r;if(i=t(n).qtip("api"),r=t(null!=i?i.elements.tooltip:void 0),r.is(":visible"))return e.push(n)}),e},n.prototype.hideTips=function(e){return t(e).qtip("hide")},n.prototype._once=function(t){var e;return e=!1,function(o){return function(){return e||t.call(o),e=!0}}(this)},n}()}).call(this)}).call(window)}).call(o,n(0))},"./common/static/xmodule/modules/js/003-3918b2d4f383c04fed8227cc9f523d6e.js":function(t,e,o){(function(t){(function(){(function(){"use strict";this.JavascriptLoader=function(){function e(){}return e.executeModuleScripts=function(e,o){var n,i,r,l,s;return o||(o=null),s=e.find(".script_placeholder"),0===s.length?(null!==o&&o(),[]):(i=function(){var t,e,o;for(o=[],t=1,e=s.length;e>=1?t<=e:t>=e;e>=1?++t:--t)o.push(!1);return o}(),n=!1,r=function(t){return function(){var e,r,l;for(e=!0,i[t]=!0,r=0,l=i.length;r<l;r++)if(!i[r]){e=!1;break}if(e&&!n&&(n=!0,null!==o))return o()}},l={},s.each(function(e,o){var n,i;return i=t(o).attr("data-src"),i in l?r(e)():(l[i]=!0,n=document.createElement("script"),n.setAttribute("src",i),n.setAttribute("type","text/javascript"),n.onload=r(e),t("head")[0].appendChild(n)),t(o).remove()}))},e}()}).call(this)}).call(window)}).call(e,o(0))},"./common/static/xmodule/modules/js/004-d47e678753905042c21bbc110fb3f8d8.js":function(t,e,o){(function(t){(function(){(function(e){"use strict";function o(e){var o,n,i;n='<a href="#" class="full full-top">See full output</a>',o='<a href="#" class="full full-bottom">See full output</a>',e.find(".longform").hide(),e.find(".shortform").append(n,o),i=e.find(".shortform-custom"),i.each(function(e,o){var n,i;i=t(o).data("open-text"),n=t(o).data("close-text"),t(o).append("<a href='#' class='full-custom'>"+i+"</a>"),t(o).find(".full-custom").click(function(t){Collapsible.toggleFull(t,i,n)})}),e.find(".collapsible header + section").hide(),e.find(".full").click(function(t){Collapsible.toggleFull(t,"See full output","Hide output")}),e.find(".collapsible header a").click(Collapsible.toggleHint)}function n(e,o,n){var i,r,l;e.preventDefault(),l=t(e.target).parent(),l.siblings().slideToggle(),l.parent().toggleClass("open"),r=t(e.target).text()===o?n:o,i=t(e.target).hasClass("full")?l.find(".full"):t(e.target),i.text(r)}function i(e){e.preventDefault(),t(e.target).parent().siblings().slideToggle(),t(e.target).parent().parent().toggleClass("open")}this.Collapsible={setCollapsibles:o,toggleFull:n,toggleHint:i}}).call(this)}).call(window)}).call(e,o(0))},13:function(t,e,o){o("./common/static/xmodule/modules/js/000-58032517f54c5c1a704a908d850cbe64.js"),o("./common/static/xmodule/modules/js/001-3ed86006526f75d6c844739193a84c11.js"),o("./common/static/xmodule/modules/js/002-e32c61651b0379c8503ad932a91e7651.js"),o("./common/static/xmodule/modules/js/003-3918b2d4f383c04fed8227cc9f523d6e.js"),t.exports=o("./common/static/xmodule/modules/js/004-d47e678753905042c21bbc110fb3f8d8.js")}},[13]));