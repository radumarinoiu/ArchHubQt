import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components" as Comp
import "pages" as Pages

ApplicationWindow {
    id: root
    width: 1000
    height: 700
    visible: true
    title: qsTr("ArchHub")

    property string currentPage: "packages"
    property string packageFilter: "all"

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 220
            Layout.fillHeight: true
            color: palette.base
            border.color: palette.mid
            border.width: 1

            Comp.Sidebar {
                id: sidebar
                currentPage: root.currentPage
                packageFilter: root.packageFilter
                onPageRequested: function(page) {
                    if (page === "packages" || page === "packages-search") {
                        root.currentPage = "packages"
                        packagesPage.showSearchBar = (page === "packages-search")
                    } else {
                        root.currentPage = page
                    }
                }
                onPackageFilterRequested: function(filter) {
                    root.packageFilter = filter
                    if (appModel)
                        appModel.packageFilter = filter
                }
            }
        }

        StackLayout {
            id: stack
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumWidth: 400
            Layout.minimumHeight: 300
            currentIndex: {
                switch (root.currentPage) {
                    case "packages": return 0
                    case "updates": return 1
                    case "mirrors": return 2
                    case "orphans": return 3
                    case "cache": return 4
                    case "settings": return 5
                    default: return 0
                }
            }

            Pages.PackagesPage { id: packagesPage }
            Pages.UpdatesPage { }
            Pages.MirrorsPage { }
            Pages.OrphansPage { }
            Pages.CachePage { }
            Pages.SettingsPage { }
        }
    }

    Component.onCompleted: {
        if (appModel) {
            appModel.refreshAll()
            appModel.packageFilter = "all"
        }
    }
}
