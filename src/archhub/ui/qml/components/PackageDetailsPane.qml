import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    id: root
    visible: appModel && appModel.selectedPackageName.length > 0

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Button {
                text: qsTr("← Back")
                visible: appModel && appModel.canGoBack
                onClicked: {
                    if (appModel)
                        appModel.goBack()
                }
            }
            Item { Layout.fillWidth: true }
        }
        Label {
            text: appModel ? appModel.packageDetailsName : ""
            font.pixelSize: 16
            font.bold: true
        }
        GridLayout {
            columns: 2
            rowSpacing: 4
            columnSpacing: 12
            Label { text: qsTr("Version:") }
            Label { text: appModel ? appModel.packageDetailsVersion : "" }
            Label { text: qsTr("Install size:") }
            Label { text: appModel ? formatSize(appModel.packageDetailsInstallSize) : "" }
            Label { text: qsTr("Last updated:") }
            Label { text: appModel ? appModel.packageDetailsLastUpdated : "" }
            Label { text: qsTr("Maintainer:") }
            Label { text: appModel ? appModel.packageDetailsMaintainer : "" }
        }
        Label {
            text: appModel ? appModel.packageDetailsDescription : ""
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
                    text: appModel ? appModel.packageDetailsDescription : ""
                    wrapMode: Text.WordWrap
                    width: parent.width - 20
                }
            }
            ListView {
                model: appModel ? appModel.depsModel : null
                delegate: ItemDelegate {
                    width: ListView.view ? ListView.view.width - 4 : 200
                    text: model.text
                    onClicked: appModel.navigateToPackage(model.text)
                }
            }
            ListView {
                model: appModel ? appModel.optionalDepsModel : null
                delegate: ItemDelegate {
                    width: ListView.view ? ListView.view.width - 4 : 200
                    text: model.text
                    onClicked: appModel.navigateToPackage(model.text)
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
