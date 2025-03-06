import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OrchestreDetailComponent } from './orchestre-detail.component';

describe('OrchestreDetailComponent', () => {
  let component: OrchestreDetailComponent;
  let fixture: ComponentFixture<OrchestreDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrchestreDetailComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OrchestreDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
