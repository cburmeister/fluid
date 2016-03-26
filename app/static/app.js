var fluid = angular.module('fluid', ['angular-loading-bar']);

fluid.config(['cfpLoadingBarProvider', function(cfpLoadingBarProvider) {
    cfpLoadingBarProvider.includeSpinner = false;
}])

fluid.controller('MediaController', function($scope, $http) {
    $http.get('/media').
        success(function(data, status, headers, config) {
            $scope.data = data;
        });

    $scope.cast = function($filename) {
        $http.get('/cast/' + $filename);
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
    $interval(get_status, 2000);

    $scope.chromecast_command = function($uri) {
        $http.get($uri);
        return false;
    }
});
