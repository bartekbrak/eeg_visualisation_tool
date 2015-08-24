# modified from https://github.com/bernii/gauge.js/ by bartekbrak
# I cut out stuff I didn't need, added setArc and modified rest to fit my use case
#
# Request Animation Frame Polyfill
# CoffeeScript version of http://paulirish.com/2011/requestanimationframe-for-smart-animating/
do () ->
	vendors = ['ms', 'moz', 'webkit', 'o']
	for vendor in vendors
		if window.requestAnimationFrame
			break
		window.requestAnimationFrame = window[vendor + 'RequestAnimationFrame']
		window.cancelAnimationFrame = window[vendor + 'CancelAnimationFrame'] or window[vendor + 'CancelRequestAnimationFrame']

	browserRequestAnimationFrame = null
	lastId = 0
	isCancelled = {}

	if not requestAnimationFrame
		window.requestAnimationFrame = (callback, element) ->
			currTime = new Date().getTime()
			timeToCall = Math.max(0, 16 - (currTime - lastTime))
			id = window.setTimeout(() ->
				callback(currTime + timeToCall)
			, timeToCall)
			lastTime = currTime + timeToCall
			return id
		# This implementation should only be used with the setTimeout()
		# version of window.requestAnimationFrame().
		window.cancelAnimationFrame = (id) ->
			clearTimeout(id)
	else if not window.cancelAnimationFrame
		browserRequestAnimationFrame = window.requestAnimationFrame
		window.requestAnimationFrame = (callback, element) ->
			myId = ++lastId
			browserRequestAnimationFrame(() ->
				if not isCancelled[myId]
					callback()
			, element)
			return myId
		window.cancelAnimationFrame = (id) ->
			isCancelled[id] = true

updateObjectValues = (obj1, obj2) ->
	for own key, val of obj2
		obj1[key] = val
	return obj1

mergeObjects = (obj1, obj2) ->
	out = {}
	for own key, val of obj1
		out[key] = val
	for own key, val of obj2
		out[key] = val
	return out

class ValueUpdater
	animationSpeed: 32
	constructor: (addToAnimationQueue=true, @clear=true) ->
		if addToAnimationQueue
			AnimationUpdater.add(@)

	update: (force=false) ->
		if force or @displayedValue != @value
			if @ctx and @clear
				@ctx.clearRect(0, 0, @canvas.width, @canvas.height)
			diff = @value - @displayedValue
			if Math.abs(diff / @animationSpeed) <= 0.001
				@displayedValue = @value
			else
				@displayedValue = @displayedValue + diff / @animationSpeed
			@render()
			return true
		return false

class BaseGauge extends ValueUpdater
	displayScale: 1

	setOptions: (options=null) ->
		@options = mergeObjects(@options, options)
		if @options.angle > .5
			@gauge.options.angle = .5
		@configDisplayScale()
		return @

	configDisplayScale: () ->
		prevDisplayScale = @displayScale

		if @options.highDpiSupport == false
			delete @displayScale
		else
			devicePixelRatio = window.devicePixelRatio or 1
			backingStorePixelRatio =
				@ctx.webkitBackingStorePixelRatio or
				@ctx.mozBackingStorePixelRatio or
				@ctx.msBackingStorePixelRatio or
				@ctx.oBackingStorePixelRatio or
				@ctx.backingStorePixelRatio or 1
			@displayScale = devicePixelRatio / backingStorePixelRatio

		if @displayScale != prevDisplayScale
			width = @canvas.G__width or @canvas.width
			height = @canvas.G__height or @canvas.height
			@canvas.width = width * @displayScale
			@canvas.height = height * @displayScale
			@canvas.style.width = "#{width}px"
			@canvas.style.height = "#{height}px"
			@canvas.G__width = width
			@canvas.G__height = height

		return @

class GaugePointer extends ValueUpdater
	displayedValue: 0
	value: 0
	options:
		length: 0.9
		strokeWidth: 0.06
		color: "#000000"

	constructor: (@gauge) ->
		@ctx = @gauge.ctx
		@canvas = @gauge.canvas
		super(false, false)
		@setOptions()

	setOptions: (options=null) ->
		updateObjectValues(@options, options)
		@length = @canvas.height * @options.length
		@strokeWidth = @canvas.height * @options.strokeWidth
		@maxValue = @gauge.maxValue
		@minValue = @gauge.minValue
		@animationSpeed =  @gauge.animationSpeed
		@options.angle = @gauge.options.angle

	render: () ->
		angle = @gauge.getAngle.call(@, @displayedValue)
		centerX = @canvas.width / 2
		centerY = @canvas.height * 0.9

		x = Math.round(centerX + @length * Math.cos(angle))
		y = Math.round(centerY + @length * Math.sin(angle))

		startX = Math.round(centerX + @strokeWidth * Math.cos(angle - Math.PI/2))
		startY = Math.round(centerY + @strokeWidth * Math.sin(angle - Math.PI/2))

		endX = Math.round(centerX + @strokeWidth * Math.cos(angle + Math.PI/2))
		endY = Math.round(centerY + @strokeWidth * Math.sin(angle + Math.PI/2))

		@ctx.fillStyle = @options.color
		@ctx.beginPath()

		@ctx.arc(centerX, centerY, @strokeWidth, 0, Math.PI*2, true)
		@ctx.fill()

		@ctx.beginPath()
		@ctx.moveTo(startX, startY)
		@ctx.lineTo(x, y)
		@ctx.lineTo(endX, endY)
		@ctx.fill()

class Gauge extends BaseGauge
	value: 20
	displayedValue: 0
	paddingBottom: 0.1
	options:
		colorBelow: "red"
		colorAbove: "green"
		angle: 0
		lineWidth: 0.45
		threshold: 0

	constructor: (@canvas, options) ->
		super()
		if typeof G_vmlCanvasManager != 'undefined'
			@canvas = window.G_vmlCanvasManager.initElement(@canvas)
		@ctx = @canvas.getContext('2d')
		@pointer = new GaugePointer(@)
		@setOptions()
		@render()

	setOptions: (options=null) ->
		super(options)
		@lineWidth = @canvas.height * (1 - @paddingBottom) * @options.lineWidth
		@radius = @canvas.height * (1 - @paddingBottom) - @lineWidth
		@ctx.clearRect(0, 0, @canvas.width, @canvas.height)
		@maxValue = @options.maxValue
		@minValue = @options.minValue
		@threshold_angle = @getAngle(@options.threshold)
		@render()
		@pointer.setOptions(@options.pointer)
		@pointer.render()
		return @

	set: (value) ->
		@pointer.value = value
		@value = value
		AnimationUpdater.run()

	getAngle: (value) ->
		return (1 + @options.angle) * Math.PI + ((value - @minValue) / (@maxValue - @minValue)) * (1 - @options.angle * 2) * Math.PI

	render: () ->
		@setArc(@displayedValue)
		@pointer.update(true)

	setArc: () ->
		w = @canvas.width / 2
		h = @canvas.height * (1 - @paddingBottom)
		@ctx.strokeStyle = @options.colorBelow
		@ctx.beginPath()
		@ctx.arc(w, h, @radius, (1 + @options.angle) * Math.PI, @threshold_angle, false)
		@ctx.lineWidth = @lineWidth
		@ctx.stroke()
		@ctx.strokeStyle = @options.colorAbove
		@ctx.beginPath()
		@ctx.arc(w, h, @radius, @threshold_angle, (2 - @options.angle) * Math.PI, false)
		@ctx.stroke()


window.AnimationUpdater =
	elements: []
	animId: null

	add: (object) ->
		AnimationUpdater.elements.push(object)

	run: () ->
		animationFinished = true
		for elem in AnimationUpdater.elements
			if elem.update()
				animationFinished = false
		if not animationFinished
			AnimationUpdater.animId = requestAnimationFrame(AnimationUpdater.run)
		else
			cancelAnimationFrame(AnimationUpdater.animId)

if typeof window.define == 'function' && window.define.amd?
	define(() ->
		{
			Gauge: Gauge,
		}
	)
else if typeof module != 'undefined' && module.exports?
	module.exports = {
		Gauge: Gauge,
	}
else
	window.Gauge = Gauge
