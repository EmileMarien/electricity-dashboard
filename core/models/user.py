"""
import 'package:housekeeper_v1/commons.dart';

class User {
  String? name;
  String? surname;
  String? password;
  String? email;
  String? referenceId;
  List<Unit>? units; //TODO: change to list with unitid's
  List<String>? unitIds;
  final String? code; //code firebaseauth excemption

  User({this.code,this.unitIds,this.name,this.surname,this.referenceId,this.units,this.password, this.email});
  
  factory User.fromSnapshot(DocumentSnapshot snapshot) {
    final newUser = User.fromJson(snapshot.data() as Map<String,dynamic>);
    newUser.referenceId = snapshot.reference.id;
    return newUser;
  }

  void setName(name){
    this.name=name;
  }

  void setSurname(surname){
    this.surname=surname;
  }

  void setUnit(Unit unit,UnitRole role){ //add unit to this User and the role with this User to the unit 
    if (units==null) {
      units=[unit];    
      } else {
      units!.add(unit);
    }

  if (unit.rolesAndUsers == null){
    unit.rolesAndUsers={role:[this]};
  } else {
    if (!unit.rolesAndUsers![role]!.contains(this)) {
      unit.rolesAndUsers![role]?.add(this);
  }

  }



  }

  void addRoleinUnit(Unit unit, UnitRole role){
    if (units==null) {
      units=[unit];   
      } else {
      if (units!.contains(unit)) {
        units!.add(unit);
      } 
      //unit.rolesAndUsers[role]=this; TODO: remove
    }
  }

  List<Unit> getUnits(){
    return units ?? [];    
  }

  String? getEmail() {return email;}

  String getName(){
    return name ?? "";
  }

  void setPassWord(String passwordInput) {
    password=passwordInput;
  }

  factory User.fromJson(Map<String,dynamic> json) => _userFromJson(json);

  Map<String,dynamic> toJson() => _userToJson(this);

  @override
  String toString() => 'User<$email>';

}

User _userFromJson(Map<String,dynamic> json) { //convert JSON file, map with types and entries for each type, to right classes 
  return User(
    email: json['email'] as String?,
    units: _unitsListFromJson(json['units']),
    name: json['name'] as String?,
    surname: json['surname'] as String?,
    password: json['password'] as String?,
  );
}

List<Unit> _unitsListFromJson(unitMap) { //convert JSON of unitlist to List of Units
  if (unitMap is List) {
      final units = <Unit>[];

    for (final unit in unitMap) {
      units.add(Unit.fromJson(unit as Map<String, dynamic>)); // every Unit is saved in JSON as Map
    }
  return units;
  } else {
    return <Unit>[];
  }

}

Map<String, dynamic> _userToJson(User instance) => <String, dynamic>{
  'email':instance.email,
  'name':instance.name,
  'surname':instance.surname,
  'password':instance.password,
  'units': _unitsListToJson(instance.units),
};

List<Map<String, dynamic>>? _unitsListToJson(List<Unit>? units) { //convert list of units to list with Maps of units (Json format)
  if (units == null) {
    return null;
  }
  final unitsList = <Map<String, dynamic>>[];
  units.forEach((unit) {
    unitsList.add(unit.toJson());
  });
  return unitsList;
}  


"""
