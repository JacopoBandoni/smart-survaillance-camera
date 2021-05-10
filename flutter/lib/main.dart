import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_smartcam/config/custom_router.dart';
import 'package:flutter_smartcam/screens/connection/connection_screen.dart';
import 'package:flutter_smartcam/services/server_service.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return RepositoryProvider(
        create: (context) => ServerService(),
        child: MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Flutter Smart Camera',
          theme: ThemeData(
            primarySwatch: Colors.blue,
            scaffoldBackgroundColor: Colors.grey[50],
            appBarTheme: AppBarTheme(
                brightness: Brightness.light,
                color: Colors.white,
                iconTheme: const IconThemeData(color: Colors.black),
                textTheme: const TextTheme(
                    headline6: TextStyle(
                        color: Colors.black,
                        fontSize: 20.0,
                        fontWeight: FontWeight.w600))),
          ),
          onGenerateRoute: CustomRouter.onGenerateRoute,
          initialRoute: ConnectionScreen.routeName,
        ));
  }
}
