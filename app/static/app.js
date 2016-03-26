var fluid = angular.module(
    'fluid', ['angular-loading-bar', 'angularLazyImg']
);

fluid.config(['cfpLoadingBarProvider', function(cfpLoadingBarProvider) {
    cfpLoadingBarProvider.includeSpinner = false;
}])

fluid.controller('MediaController', function($scope, $http) {
    console.log('Querying Chromecast status...');
    $http.get('/media').
        success(function(data, status, headers, config) {
            $scope.data = data;
        });

    $scope.cast = function($filename) {
        console.log('Casting media on Chromecast...');
        $http.get('/cast/' + $filename);
        console.log('/cast/' + $filename);
        return false;
    }
});

fluid.controller('ChromecastController', function($scope, $interval, $http) {
    var get_status = function() {
        $http.get('/chromecast/status').
            success(function(data, status, headers, config) {
                $scope.data = data;
            });
    }
    get_status();
    $interval(get_status, 5000);

    $scope.play = function() {
        console.log('Playing media on Chromecast...');
        $http.get('/play');
        return false;
    }
    $scope.pause = function() {
        console.log('Pausing media on Chromecast...');
        $http.get('/pause');
        return false;
    }
    $scope.stop = function() {
        console.log('Stopping media on Chromecast...');
        $http.get('/stop');
        return false;
    }
    $scope.backward = function() {
        console.log('Seeking backward through media on Chromecast...');
        $http.get('/backward');
        return false;
    }
    $scope.forward = function() {
        console.log('Seeking forward through media on Chromecast...');
        $http.get('/forward');
        return false;
    }
});
