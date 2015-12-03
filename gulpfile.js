var gulp = require('gulp');
var source = require('vinyl-source-stream'); // Used to stream bundle for further handling
var browserify = require('browserify');
var watchify = require('watchify');
var reactify = require('reactify'); 
var concat = require('gulp-concat');
 
gulp.task('browserify', function() {
    var bundler = browserify({
        entries: [
            /*'./feedme/static/js/feedme/Buttons.jsx',
            './feedme/static/js/feedme/OrderLine.jsx',
            './feedme/static/js/feedme/OrderLineList.jsx',
            './feedme/static/js/feedme/OrderLineForm.jsx',
            './feedme/static/js/feedme/Order.jsx',*/
            './feedme/static/js/feedme/feedme.jsx'], // Only need initial file, browserify finds the deps
        transform: [reactify], // We want to convert JSX to normal javascript
        debug: true, // Gives us sourcemapping
        cache: {}, packageCache: {}, fullPaths: true // Requirement of watchify
    });
    var watcher  = watchify(bundler);
        return watcher
            .on('update', function () { // When any files update
                var updateStart = Date.now();
                console.log('Updating!');
                watcher.bundle() // Create new bundle that uses the cache for high performance
                    .pipe(source('feedme.min.js'))
                    // This is where you add uglifying etc.
                    .pipe(gulp.dest('./feedme/static/js/'));
                console.log('Updated!', (Date.now() - updateStart) + 'ms');
            })
            .bundle() // Create the initial bundle when starting the task
            .pipe(source('feedme.min.js'))
            .pipe(gulp.dest('./feedme/static/js/'));
 });

// I added this so that you see how to run two watch tasks
gulp.task('css', function () {
    gulp.watch('styles/**/*.css', function () {
        return gulp.src('styles/**/*.css')
        .pipe(concat('main.css'))
        .pipe(gulp.dest('build/'));
    });
 });

 // Just running the two tasks
 gulp.task('default', ['browserify']);
