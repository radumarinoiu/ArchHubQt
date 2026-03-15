import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    id: root
    visible: appModel && appModel.selectedPackageName.length > 0

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        Label {
            text: appModel ? appModel.getPackageDetailsName() : ""
            font.pixelSize: 16
            font.bold: true
        }
        GridLayout {
            columns: 2
            rowSpacing: 4
            columnSpacing: 12
            Label { text: qsTr("Version:") }
            Label { text: appModel ? appModel.getPackageDetailsVersion() : "" }
            Label { text: qsTr("Install size:") }
            Label { text: appModel ? formatSize(appModel.getPackageDetailsInstallSize()) : "" }
            Label { text: qsTr("Last updated:") }
            Label { text: appModel ? appModel.getPackageDetailsLastUpdated() : "" }
            Label { text: qsTr("Maintainer:") }
            Label { text: appModel ? appModel.getPackageDetailsMaintainer() : "" }
        }
        Label {
            text: appModel ? appModel.getPackageDetailsDescription() : ""
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        TabBar {
            id: tabBar
            Layout.fillWidth: true
            TabButton { text: qsTr("Details") }
            TabButton { text: qsTr("Dependencies") }
            TabButton { text: qsTr("Optional Deps") }
            TabButton { text: qsTr("Conflicts") }
        }
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            ScrollView {
                Label {
                    text: appModel ? appModel.getPackageDetailsDescription() : ""
                    wrapMode: Text.WordWrap
                    width: parent.width - 20
                }
            }
            ListView {
                model: appModel ? appModel.depsModel : null
                delegate: ItemDelegate {
                    width: ListView.view ? ListView.view.width - 4 : 200
                    text: model.text
                    onClicked: appModel.selectedPackageName = model.text
                }
            }
            ListView {
                model: appModel ? appModel.optionalDepsModel : null
                delegate: ItemDelegate {
                    width: ListView.view ? ListView.view.width - 4 : 200
                    text: model.text
                    onClicked: appModel.selectedPackageName = model.text
                }
            }
            ListView {
                model: appModel ? appModel.conflictsModel : null
                delegate: ItemDelegate {
                    width: ListView.view ? ListView.view.width - 4 : 200
                    text: model.text
                }
            }
        }
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + " B"
        if (bytes < 1024*1024) return (bytes / 1024).toFixed(1) + " KiB"
        return (bytes / (1024*1024)).toFixed(1) + " MiB"
    }
}
