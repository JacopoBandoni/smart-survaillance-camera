import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_smartcam/screens/nav/cubit/bottom_nav_bar_cubit.dart';
import 'package:flutter_smartcam/screens/nav/nav_screens/frame_overview_screen/frame_overview_screen.dart';
import 'package:flutter_smartcam/screens/nav/nav_screens/streaming_screen/streamin_screen.dart';

import 'bottom_nav_bar.dart';
import 'bottom_nav_item.dart';

class NavScreen extends StatelessWidget {
  static const String routeName = "/nav";

  static Route route() {
    return PageRouteBuilder(pageBuilder: (_, __, ___) {
      return BlocProvider<BottomNavBarCubit>(
        create: (_) => BottomNavBarCubit(),
        child: NavScreen(),
      );
    });
  }

  final Map<BottomNavItem, IconData> items = const {
    BottomNavItem.frameOverview: Icons.photo,
    BottomNavItem.videoStream: Icons.videocam,
  };

  final Map<BottomNavItem, Widget> screens = {
    BottomNavItem.frameOverview: FrameOverviewScreen(),
    BottomNavItem.videoStream: StreamingScreen(),
  };

  final Map<BottomNavItem, String> title = {
    BottomNavItem.frameOverview: "Frame Overview",
    BottomNavItem.videoStream: "Streaming Video",
  };

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async => false,
      child: BlocBuilder<BottomNavBarCubit, BottomNavBarState>(
          builder: (context, state) => Scaffold(
                appBar: AppBar(
                  title: Text(title[state.selectedItem]),
                  leading: Container(),
                  actions: [
                    IconButton(
                      icon: Icon(Icons.arrow_back),
                      onPressed: () => Navigator.pop(context),
                    )
                  ],
                ),
                body: screens[state.selectedItem],
                bottomNavigationBar: BottomNavBar(
                  items: items,
                  selectedItem: state.selectedItem,
                  onTap: (index) {
                    final selectedItem = BottomNavItem.values[index];
                    context
                        .read<BottomNavBarCubit>()
                        .updateSelectedItem(selectedItem);
                  },
                ),
              )),
    );
  }
}
