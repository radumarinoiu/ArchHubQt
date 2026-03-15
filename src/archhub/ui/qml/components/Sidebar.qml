import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    property string currentPage: "packages"
    property string packageFilter: "all"
    signal pageRequested(string page)
    signal packageFilterRequested(string filter)

    spacing: 8

    ColumnLayout {
        Layout.fillWidth: true
        Layout.margins: 8
        spacing: 4
        CounterCard { label: qsTr("Packages"); value: appModel ? appModel.totalPackages : 0 }
        CounterCard { label: qsTr("AUR"); value: appModel ? appModel.aurPackages : 0 }
        CounterCard { label: qsTr("Updates"); value: appModel ? appModel.updatesCount : 0 }
    }

    Label {
        Layout.leftMargin: 12
        Layout.topMargin: 4
        text: qsTr("Packages")
        font.bold: true
        font.pixelSize: 11
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("All Packages")
        flat: true
        highlighted: root.packageFilter === "all"
        onClicked: { root.packageFilterRequested("all"); root.pageRequested("packages"); }
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("Pacman")
        flat: true
        highlighted: root.packageFilter === "pacman"
        onClicked: { root.packageFilterRequested("pacman"); root.pageRequested("packages"); }
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("AUR")
        flat: true
        highlighted: root.packageFilter === "aur"
        visible: appModel && appModel.aurPackages > 0
        onClicked: { root.packageFilterRequested("aur"); root.pageRequested("packages"); }
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("Search Packages")
        flat: true
        onClicked: root.pageRequested("packages-search")
    }

    Label {
        Layout.leftMargin: 12
        Layout.topMargin: 8
        text: qsTr("System")
        font.bold: true
        font.pixelSize: 11
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("Updates")
        flat: true
        highlighted: root.currentPage === "updates"
        onClicked: root.pageRequested("updates")
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("Mirrors")
        flat: true
        highlighted: root.currentPage === "mirrors"
        onClicked: root.pageRequested("mirrors")
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("Find Orphans")
        flat: true
        highlighted: root.currentPage === "orphans"
        onClicked: root.pageRequested("orphans")
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("Clear Cache")
        flat: true
        highlighted: root.currentPage === "cache"
        onClicked: root.pageRequested("cache")
    }
    Button {
        Layout.fillWidth: true
        Layout.margins: 4
        text: qsTr("Settings")
        flat: true
        highlighted: root.currentPage === "settings"
        onClicked: root.pageRequested("settings")
    }

    Item { Layout.fillHeight: true }
}
