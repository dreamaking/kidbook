function WXCard(opt){
	this.opt 	= opt || {};
	this.action	= this.opt.action 	|| ["addCard"];
	this.success= this.opt.success	|| function(){};
	this.cardId = this.opt.cardId || "pfdNtt5N1WHzQf_Luo7EyWkMwjeY";
	this.wait = new Wait("正在校验卡券，请稍候...");

	this.getSignature();
}

WXCard.prototype = {

	getSignature : function(){
		var self = this,
			u = window.cfg.getSignature,
			noncestr = "kidbook",
			timestamp = Math.floor(new Date().getTime() / 1000),
			url = encodeURIComponent( location.href.split('#')[0] );
		if(!u) return;
		u += ("?noncestr=" + noncestr);
		u += ("&timestamp=" + timestamp);
		u += ("&url=" + url);
		$.get(u, function(data){
			if(data.code == 200 && data.signature){
				self.init(timestamp, noncestr, data.signature);
			}else{
				// alert("get signature fail..");
			}
		}, "json");
	},

	init : function(t, n, s){
		var self = this;
		wx.config({
		    debug: false,
		    appId : "wxf9dc3c84d5f267f2",
		    timestamp: t,
		    nonceStr: n,
		    signature: s,
		    jsApiList: self.action
		});
		wx.ready(function(){
			self.getCardExt();
		});
	},

	addCard : function( callback ){
		var self = this;
		if( !self.cardExt ) return;
		wx.addCard({
		    cardList: [{
		        cardId: self.cardId,
		        cardExt: JSON.stringify( self.cardExt )
		    }],
		    success: function (res) {
		        var cardList = res.cardList;
		        callback.call( self, res );
		        // location.href = window.cfg.accept;
		    }
		});
	},

	getCardExt : function(){
		var self = this,
			url = window.cfg.getCardSignature,
			param = {};
		param.timestamp = Math.floor(new Date().getTime() / 1000);
		param.code = param.timestamp;
		param.card_id = self.cardId;
		param.openid = self.getOpenId();
		param.balance = "";
		$.get(url, param, function(data){
			if(data.code == 200 && data.signature){
				self.setCardExt(param, data.signature);
				self.wait.hide();
			}
		}, "json");
	},

	setCardExt : function(param, signature){
		var self = this;
		self.cardExt = {};
		self.cardExt.code = param.code;
		self.cardExt.openid = param.openid;
		self.cardExt.timestamp = param.timestamp;
		self.cardExt.signature = signature;
	},

	getOpenId : function(){
		return $.fn.cookie("visitor_openid") || $("#visitor_openid").val();
	}
};