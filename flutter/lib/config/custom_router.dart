import 'package:flutter/material.dart';
import 'package:flutter_smartcam/screens/connection/connection_screen.dart';
import 'package:flutter_smartcam/screens/nav/nav_screen.dart';

class CustomRouter {
  static Route onGenerateRoute(RouteSettings settings) {
    print('Route: ${settings.name}');

    switch (settings.name) {
      case '/':
        return MaterialPageRoute(
            settings: settings, builder: (_) => const Scaffold());
      case NavScreen.routeName:
        return NavScreen.route();
      case ConnectionScreen.routeName:
        return ConnectionScreen.route();
      default:
        throw Error();
    }
  }
}
