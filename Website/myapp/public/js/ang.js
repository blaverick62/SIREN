/**
 * Created by blaverick on 12/14/16.
 */
var app = angular.module('siren', []);
app.controller('sirenctrl', function ($scope) {
    $scope.charts = [$('#ip-bar'), $('#user-bar'), $('#password-bar'), $('#success-pie'), $('#password-pie')]
});